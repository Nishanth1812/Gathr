import os
os.urandom(24).hex()
print("Generated Key: ", os.urandom(24).hex())