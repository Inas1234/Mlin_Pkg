clean:
	rm -rf build
	rm -rf include/*

install:
	/opt/homebrew/bin/python3.11 /Users/inas/Desktop/Programming/Python/MlinPkg/main.py install https://github.com/Taywee/args    


test:
	g++ main.cpp   -std=c++17 -lpthread   -o main