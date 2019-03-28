# ---- Link ---------------------------
modsum.so:  modsum.o  modsum.mak
	gcc -shared -o modsum.so  modsum.o `pkg-config --libs python3`

# ---- gcc C compile ------------------
modsum.o:  modsum.c modsum.h modsum.mak
	gcc -O3 -flto -march=native -fPIC -c modsum.c -I /usr/include/python3.7m/ -I /usr/lib64/python3.7/site-packages/numpy/core/include/numpy
