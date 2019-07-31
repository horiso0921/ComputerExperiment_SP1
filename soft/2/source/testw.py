import sys
import bisect
from collections import deque
from collections import defaultdict
bisect_left = bisect.bisect_left
bisect_right = bisect.bisect_right

def main(lines):
  v,e,x,y = map(int, lines[0].split())
  n = list(map(int, lines[1].split()))
  m = list(map(int, lines[2].split()))
  edg = [[] for i in range(v)]
  for ab in lines[3:]:
    a,b = map(int, ab.split())
    edg[a-1].append(b-1)
    edg[b-1].append(a-1)
  check = [True for i in range(v)]
  times = [0 for i in range(v)]
  new_q = deque()
  time = 0
  for i in range(x):
    times[n[i]-1] = m[i]
    check[n[i]-1] = False
    new_q.append(n[i] - 1)
  while new_q:
    q = new_q
    new_q = deque()
    bf = defaultdict(int)
    while q:
      edg_v = q.pop()
      for i in edg[edg_v]:
        if check[i]:
          bf[i] = max(bf[i], times[edg_v])
    for key,value in bf.items():
      times[key] = value+time+1
      check[key] = False
      new_q.append(key)
    time += 1
  times.sort()
  print(v-bisect_right(times,y))
  return



if __name__ == '__main__':
    lines = []
    for l in sys.stdin:
        lines.append(l.rstrip('\r\n'))
    main(lines)
