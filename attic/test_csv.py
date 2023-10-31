import os

file = '/Users/mehmetmertbese/Desktop/NextGSim/results/RAN.csv'
print(file)
print(os.getcwd())
with open(file, "rb") as f:
    while True:
        bytes_read = f.read(4096)
        print('Client: Bytes Read')
        print(bytes_read)
        if not bytes_read:
            # file transmitting is done
            print('COMPLETION')
            break
