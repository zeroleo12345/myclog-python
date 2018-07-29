// myclog-python.cpp : 定义 DLL 应用程序的导出函数。
//

#include "Python.h"
#include "myclog.h"

#ifdef _DEBUG  
#pragma comment(lib, "python27_d.lib")
#else
#pragma comment(lib, "python27.lib")
#endif

//PyObject *dict = PyDict_New();
//PyDict_SetItemString(dict, "message", PyString_FromString(pmsg));  //PyInt_FromLong(0)
PyObject * g_except = PyErr_NewException("myclog.Exception", NULL, NULL);
char tips[128];
int ret;
//全局唯一日志类
MyCLog g_log;

static PyObject* myclog(PyObject* self, PyObject* args) {
	MyCLog *log = &g_log;
	return PyCapsule_New(log, NULL, NULL);
}

/*
	myclog.setLogHeader("prefix")
*/
static PyObject* setLogHeader(PyObject* self, PyObject* args) {
	char * prefix;
	if (!PyArg_ParseTuple(args, "s", &prefix)){
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.setLogHeader(prefix);
	if (ret < 0) {
		sprintf(tips, "setLogHeader ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
myclog.setLogLevel("trace", "close")
*/
static PyObject* setLogLevel(PyObject* self, PyObject* args) {
	char * file_level;
	char * term_level = "close";
	if (!PyArg_ParseTuple(args, "s", &file_level)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.setLogLevel(file_level, term_level);
	if (ret < 0) {
		sprintf(tips, "setLogLevel ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
	myclog.setLogDir("/log")  # Linux
	myclog.setLogDir("E:\\cygwin64\\home\\zlx\\code\\baicai\\myclog-python\\x64\\Release")	# Windows
*/
static PyObject* setLogDir(PyObject* self, PyObject* args) {
	char * log_path;
	if (!PyArg_ParseTuple(args, "s", &log_path)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.setLogDir(log_path);
	if (ret < 0) {
		sprintf(tips, "setLogDir ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
myclog.setLogMaxLine(100000)
*/
static PyObject* setLogMaxLine(PyObject* self, PyObject* args) {
	int max_line;
	if (!PyArg_ParseTuple(args, "i", &max_line)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.setLogMaxLine(max_line);
	if (ret < 0) {
		sprintf(tips, "setLogMaxLine ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
myclog.setLogBufferSize(1024)
*/
static PyObject* setLogBufferSize(PyObject* self, PyObject* args) {
	int buff_size;
	if (!PyArg_ParseTuple(args, "i", &buff_size)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.setLogBufferSize(buff_size);
	if (ret < 0) {
		sprintf(tips, "setLogBufferSize ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
	myclog.flush()
*/
static PyObject* flush(PyObject* self, PyObject* args) {
	ret = g_log.flush();
	if (ret < 0) {
		sprintf(tips, "flush ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
myclog.close()
*/
static PyObject* close(PyObject* self, PyObject* args) {
	ret = g_log.close();
	if (ret < 0) {
		sprintf(tips, "close ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

/*
fileno = myclog.get_fileno()
*/
static PyObject* get_fileno(PyObject* self, PyObject* args) {
	ret = g_log.get_fileno();
	if (ret < 0) {
		sprintf(tips, "get_fileno ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
    return Py_BuildValue("i", ret);
}

/*
	myclog.trace("log text, %s, %d", msg, int)
*/
static PyObject* trace(PyObject* self, PyObject* args) {
	Py_RETURN_NONE;
}

/*
myclog.trace(format="log text, %s, %d", msg, int)
*/
static PyObject* db(PyObject* self, PyObject* args) {
	if (!g_log.isHigherFileLevel(log_debug))
		Py_RETURN_NONE;
	
	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.logWithoutFormat(log_debug, content);
	if (ret < 0) {
		sprintf(tips, "log ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* info(PyObject* self, PyObject* args) {
	if (!g_log.isHigherFileLevel(log_info))
		Py_RETURN_NONE;

	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.logWithoutFormat(log_info, content);
	if (ret < 0) {
		sprintf(tips, "logWithoutFormat ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* warn(PyObject* self, PyObject* args) {
	if (!g_log.isHigherFileLevel(log_warn))
		Py_RETURN_NONE;
	
	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.logWithoutFormat(log_warn, content);
	if (ret < 0) {
		sprintf(tips, "logWithouteFormat ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* error(PyObject* self, PyObject* args) {
	if (!g_log.isHigherFileLevel(log_error))
		Py_RETURN_NONE;
	
	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.logWithoutFormat(log_error, content);
	if (ret < 0) {
		sprintf(tips, "logWithoutFormat ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* critical(PyObject* self, PyObject* args) {
	if (!g_log.isHigherFileLevel(log_critical))
		Py_RETURN_NONE;

	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.logWithoutFormat(log_critical, content);
	if (ret < 0) {
		sprintf(tips, "logWithoutFormat ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* println(PyObject* self, PyObject* args) {
	//TODO: 待完善level
	if (!g_log.isHigherPrintLevel(log_critical))
		Py_RETURN_NONE;

	char * content;
	if (!PyArg_ParseTuple(args, "s", &content)) {
		PyErr_SetString(g_except, "PyArg_ParseTuple Error");
		return NULL;
	}
	ret = g_log.println(log_critical, content);
	if (ret < 0) {
		sprintf(tips, "println ret: %d", ret);
		PyErr_SetString(g_except, tips);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef myclog_methods[] = {
	//{ "myclog", myclog, METH_VARARGS },
	{ "setLogHeader", setLogHeader, METH_VARARGS },
	{ "setLogDir", setLogDir, METH_VARARGS },
	{ "setLogBufferSize", setLogBufferSize, METH_VARARGS },
	{ "setLogMaxLine", setLogMaxLine, METH_VARARGS },
	{ "setLogLevel", setLogLevel, METH_VARARGS },
	
	{ "flush", flush, METH_NOARGS },
	{ "close", close, METH_NOARGS },
	{ "get_fileno", get_fileno, METH_NOARGS },

	{ "trace", trace, METH_VARARGS },
	{ "db", db, METH_VARARGS },
	{ "info", info, METH_VARARGS },
	{ "warn", warn, METH_VARARGS },
	{ "error", error, METH_VARARGS },
	{ "critical", critical, METH_VARARGS },
	
	{ "println", println, METH_VARARGS },
	{ NULL, NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "myclog",     // m_name
    "C log with buffer",  // m_doc
    -1,                  // m_size
    myclog_methods,    // m_methods
    //NULL,                // m_reload
    //NULL,                // m_traverse
    //NULL,                // m_clear
    //NULL,                // m_free
};
PyMODINIT_FUNC PyInit_myclog(void) {
    PyModule_Create(&moduledef);
}
#else
PyMODINIT_FUNC initmyclog(void)
{
	Py_InitModule3("myclog", myclog_methods, "C log with buffer");
}
#endif
