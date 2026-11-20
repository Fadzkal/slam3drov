import sqlite3
import numpy as np

conn = sqlite3.connect('/home/fadzkal_luthfi/.ros/rtabmap.db')
c = conn.cursor()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print('Tables in rtabmap.db:', tables)

# Node table has pose and stamp!
# Let's inspect Node table columns
for t in ['Node', 'Link', 'Map_info', 'Data']:
    if t in tables:
        cols = [col[1] for col in c.execute(f"PRAGMA table_info({t});").fetchall()]
        print(f"Table {t} columns:", cols)

# Count nodes
count = c.execute("SELECT count(*) FROM Node;").fetchone()[0]
print(f"Total Nodes in rtabmap.db: {count}")

# Fetch nodes: id, stamp, pose
rows = c.execute("SELECT id, stamp, pose FROM Node ORDER BY stamp ASC;").fetchall()
print(f"Fetched {len(rows)} nodes")
if rows:
    sample_pose = rows[0][2]
    print(f"Sample pose type: {type(sample_pose)}, len: {len(sample_pose) if sample_pose else 0}")
