in_query_addr = """
	  SELECT
			  txout.address
			  FROM txin
			  LEFT JOIN txout ON (txout.txout_id = txin.txout_id)
			 WHERE txin.tx_id = ?
"""
in_query_addr_with_value = """
	  SELECT
			  txout.address, txout.txout_value
			  FROM txin
			  LEFT JOIN txout ON (txout.txout_id = txin.txout_id)
			 WHERE txin.tx_id = ?
"""
out_query_addr = """
	  SELECT
			  txout.address
			  FROM txout
			  LEFT JOIN txin ON (txin.txout_id = txout.txout_id)
			 WHERE txout.tx_id = ?
"""
tx_hash_query = """
	  SELECT
			  tx_hash
			  FROM tx
			  WHERE tx_id = ?
"""
out_query_addr_with_value = """
	  SELECT
			  txout.address, txout.txout_value
			  FROM txout
			  LEFT JOIN txin ON (txin.txout_id = txout.txout_id)
			 WHERE txout.tx_id = ?
"""
time_query = """
	  SELECT
			  time
			  FROM tx
			  LEFT JOIN blocks ON (tx.block_id = blocks.block_id)
			 WHERE tx.tx_id = ?
"""

number_of_transactions_address_so_far_query = "SELECT COUNT(*) FROM txout TOUT JOIN txin TI ON TOUT.tx_id = TI.tx_id WHERE TOUT.tx_id < ? AND TOUT.address = ?"
used_so_far_query = "SELECT EXISTS(SELECT * FROM txout TOUT JOIN txin TI ON TOUT.tx_id = TI.tx_id WHERE TOUT.tx_id < ? AND TOUT.address = ?)"

# Return the amount of transactions that is associate with those block times within a interval of time.
number_of_transactions_between_time_interval = """
						SELECT count(*) 
							FROM tx LEFT JOIN blocks 
							ON (tx.block_id = blocks.block_id) 
						WHERE blocks.time >= ? AND blocks.time <= ?
"""

# Return the minimum and maximum transaction ids associate wih blocks inside a given time interval.
max_min_transaction_ids_time_interval = """
					SELECT MIN(tx.tx_id), MAX(tx.tx_id) 
						FROM tx LEFT JOIN blocks 
						ON (tx.block_id = blocks.block_id) 
					WHERE blocks.time >= ? AND blocks.time <= ?
"""

txhash_to_txid_query = "SELECT tx_id FROM tx WHERE tx_hash = ?"""
max_txid_query = "SELECT MAX(tx_id) FROM tx"
max_block_query = "SELECT MAX(block_id) FROM blocks"
last_seen_query = "SELECT last_seen FROM addresses WHERE address = ?"
get_features_query = "SELECT * FROM addresses WHERE address = ?"

features_schema_prepend = """
PRAGMA page_size = 4096;
CREATE TABLE IF NOT EXISTS addresses(
address TEXT NOT NULL PRIMARY KEY,
first_seen INT,
last_seen INT,
recv INT,
sent INT,
balance INT,
n_tx INT,
"""

features_clusters_schema_prepend = """
CREATE TABLE IF NOT EXISTS clusters(
cluster_id INT NOT NULL PRIMARY KEY,
first_seen INT,
last_seen INT,
recv INT,
sent INT,
n_tx INT,
"""

features_update_partial_query = "UPDATE addresses SET BITCOINTALK_USER = ?, BITCOINOTC_USER = ?, SCAMMER = ?, SHAREHOLDER = ?, CASASCIUS = ?, FBI = ?, SILKROAD = ?, KILLER = ?, MALWARE = ?, cluster_id = ? WHERE address = ?"

def update_features(n, table):
	return "INSERT OR REPLACE INTO %s VALUES (" % table + '?,'*(n-1) + '?)'

cluster_labels_schema = """
CREATE TABLE IF NOT EXISTS cluster_labels(
cluster_id INT NOT NULL PRIMARY KEY,
label TEXT NOT NULL)
"""

get_cluster_label_query = "SELECT label FROM cluster_labels WHERE cluster_id = ?"

add_cluster_label_query = """
INSERT OR REPLACE INTO 
cluster_labels 
VALUES (?, ?)
"""

