clean:
	rm -rf build
	rm -rf include/*
	rm packages.json

installA:
	/opt/homebrew/bin/python3.11 /Users/inas/Desktop/Programming/Python/MlinPkg/main.py install -u https://github.com/SRombauts/SQLiteCpp    

install:
	/opt/homebrew/bin/python3.11 /Users/inas/Desktop/Programming/Python/MlinPkg/main.py install nlohmann    


test:
	g++ main.cpp ./build//SQLiteCpp/libSQLiteCpp.a   -std=c++17 -lpthread   -o main