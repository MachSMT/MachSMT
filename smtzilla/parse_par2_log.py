import sys


data = {}


for line in sys.stdin.readlines():
    line = line.split()
    if line[0] not in data:
        data[line[0]] = {}
    if line[1] not in data[line[0]]:
        data[line[0]][line[1]] = {}
    solver = ''
    for i in range(2,len(line)-1):
        solver += line[i] + ' '
    solver = solver[:-1]
    data[line[0]][line[1]][solver] = float(line[-1])

improve = []
hurt = []
for theory in data:
    for track in data[theory]:
        print()
        print(theory,track)
        print()
        smtzilla = None
        vb = None
        sa = float('+inf')
        results = []
        for solver in data[theory][track]:
            results.append((solver,data[theory][track][solver]))
        results.sort(key=lambda v:v[1])
        for solver,par2 in results:
            print(solver,par2)
            if solver == 'SMTZILLA':
              smtzilla = par2
            elif solver == 'Virtual Best':
              vb = par2
            else:
              sa = min(sa,par2)
        per = 100.0 * (sa - smtzilla) / sa
        if per > 0:
          improve.append((theory,track,per))
        else:
          hurt.append((theory,track,per))
        print('Improve on Standalone by: ' + str((per)))
        print('----------------------------')

print('--------------')
print(' improve')
print('--------------')

for v in improve:
    print(v)


print('--------------')
print(' hurt')
print('--------------')

for v in hurt:
    print(v)
