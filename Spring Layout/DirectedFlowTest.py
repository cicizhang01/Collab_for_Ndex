import ndex.beta.layouts as layout
import time
from ndex.networkn import NdexGraph

uuidTest= "153b6970-6193-11e5-8ac5-06603eb7f303"
M = NdexGraph(server='http://ndexbio.org', uuid=uuidTest )

start = time.time()
layout.apply_directed_flow_layout(M, iterations= 500)
elapsed_time = time.time() - start
print elapsed_time
M.upload_to('http://www.ndexbio.org/', 'cc.zhang', 'piggyzhang')