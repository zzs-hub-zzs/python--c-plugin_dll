#include <pybind11/embed.h>
#include <string>
#include <mutex>

namespace py = pybind11;

static std::once_flag init_flag;
static py::scoped_interpreter* guard_ptr = nullptr;

void init_python()
{
    guard_ptr = new py::scoped_interpreter();
}

extern "C" __declspec(dllexport)
const char* run_algo(const char* algo_name, const char* json_str)
{
    static std::string result;

    try
    {
        std::call_once(init_flag, init_python);

        py::gil_scoped_acquire acquire;

        py::module sys = py::module::import("sys");
        sys.attr("path").attr("insert")(0, ".");

        py::module json = py::module::import("json");
        py::module router = py::module::import("algo_router");

        py::object data = json.attr("loads")(json_str);

        py::object res = router.attr("run")(algo_name, data);

        result = json.attr("dumps")(res).cast<std::string>();

        return result.c_str();
    }
    catch (py::error_already_set& e)
    {
        result = std::string("{\"errorCode\":500,\"errorMsg\":\"") + e.what() + "\"}";
        return result.c_str();
    }
    catch (std::exception& e)
    {
        result = std::string("{\"errorCode\":500,\"errorMsg\":\"") + e.what() + "\"}";
        return result.c_str();
    }
}