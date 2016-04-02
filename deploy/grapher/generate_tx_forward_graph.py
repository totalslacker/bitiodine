#!/usr/bin/env python3
import networkx as nx

import argparse
import math

import os, sys
lib_path = os.path.abspath('../common')
sys.path.append(lib_path)

from sqlite_wrapper import SQLiteWrapper
from queries import *
from util import *
from collections import Counter


def dump_transactions(G, tx_id, tx_count, count):
  print ("dump_transactions: tx_id=%d count=%d" % (tx_id, count))
  if count == 0:
    print("done")
    return tx_count

  try:
    in_res = db.query(in_query_addr_with_value, (tx_id,))
    out_res = db.query(out_query_addr_with_value, (tx_id,))
    tx_hash = db.query(tx_hash_query, (tx_id,), fetch_one=True)
  except Exception as e:
    print(e)
    # Just go to the next transaction

  in_addr = set()
  out_addr = set()
  in_values = {}
  out_values = {}

  # no in address on generated coins
  if len(in_res) == 0:
    in_addr.add("GENERATED")

  for line in in_res:
    address = line[0]
    value = line[1] / 100000000.0
    print("in address=%s value=%f" % (address, value))
    if address is None:
      address = "GENERATED"
    in_addr.add(address)
    in_values[address] = value

  # OUT  
  out_sum = 0.0
  for out in out_res:
    address = out[0]
    value = out[1] / 100000000.0
    txout_id = out[2]
    print("out address=%s value=%f" % (address, value))
    if out not in in_addr:
      out_addr.add(address)
    out_values[address] = {'value' : value, 'txout_id' : txout_id}
    out_sum += value;

  for in_address in in_addr:
    G.add_node(in_address)

  for out_address in out_addr:
    G.add_node(out_address)

  for in_address in in_addr:
    for out_address in out_addr:
      out_value = out_values[out_address]['value']
      in_value = in_values[in_address]
      value = in_value * out_value / out_sum
      print("out address=%s" % (out_address))
      if in_address != out_address:
        G.add_edge(in_address, out_address, tx_id=tx_id, tx_hash=tx_hash, tx_value=value)
        tx_count += 1
        print("%s -> %s value=%d" % (in_address, out_address, value))

  # iterate through the outputs and dump all of them (plus their children depending on count)
  for out_address in out_addr:
      txout_id = out_values[out_address]['txout_id']
      print("%s: txout_id=%d" % (out_address, txout_id))
      in_res = db.query("select txin_id, tx_id from txin where txout_id=?", (txout_id,))
      print('\tin_res=', in_res)
      if len(in_res) > 0:
        print("\t txin_id=%d tx_id=%d" % (in_res[0][0], in_res[0][1]))
        tx_count = dump_transactions(G, in_res[0][1], tx_count, count - 1)

  return tx_count


###

db = SQLiteWrapper('../blockchain/blockchain.sqlite')

parser = argparse.ArgumentParser(description='Generate transaction graph based on transactions on a time interval desired')
parser.add_argument("--tx", dest="base_tx", default="F4184FC596403B9D638783CF57ADFE4C75C605F6356FBC91338530E9831E9E16")
parser.add_argument("--count", dest="count", default=1, type=int)
parser.add_argument("--out-filename", dest="output_filename", default="tx_graph")
args = parser.parse_args()

try:
  base_tx_id = db.query(txhash_to_txid_query, (args.base_tx,))[0][0]
except Exception as e:
  die(e)

G = nx.MultiDiGraph()

print("base_tx_id=%d count=%d" %(base_tx_id, args.count))

tx_count = dump_transactions(G, base_tx_id, 0, args.count)

print("tx_count=%d" % (tx_count))
save(G, args.output_filename, tx_count)
