cmake_minimum_required(VERSION 3.15)

project(algo_plugin)

set(CMAKE_CXX_STANDARD 17)

# 查找 pybind11
find_package(pybind11 REQUIRED)

# 构建 DLL
add_library(algo_router SHARED plugin.cpp)

# 链接 Python 嵌入库
target_link_libraries(algo_router PRIVATE pybind11::embed)