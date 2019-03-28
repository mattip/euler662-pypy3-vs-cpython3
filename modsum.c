/* A file to test imorting C modules for handling arrays to Python */

#include "Python.h"
#include "arrayobject.h"
#include "modsum.h"
#include <math.h>

/* #### Globals #################################### */

/* ==== Set up the methods table ====================== */
static struct PyMethodDef _modsumMethods[] = {
	{"np_modsum", np_modsum, METH_VARARGS, "modsum"},
	{NULL, NULL, 0, NULL}     /* Sentinel - marks the end of this structure */
};

static struct PyModuleDef _modsum_mod = {
            PyModuleDef_HEAD_INIT,
            "_modsum",
            NULL,
            -1,
            _modsumMethods
        };


/* ==== Initialize the C_test functions ====================== */
// Module name must be _modsum in compile and linked
PyMODINIT_FUNC
PyInit_modsum()  {
	PyObject* ret = PyModule_Create(&_modsum_mod);
	import_array();  // Must be present for NumPy.  Called first after above line.
    return ret;
}

/* ==== Create 1D Carray from PyArray ======================
    Assumes PyArray is contiguous in memory.             */
static inline uint64_t *pyvector_to_Carrayptrs(PyArrayObject *arrayin)  {
	return (uint64_t *) arrayin->data;  /* pointer to arrayin data as double */
}

int my_modsum(
	const uint64_t *const cin,
    const size_t n)
{
    unsigned __int128 sum = 0;
	/* Operate on the vectors  */
	for ( size_t i=0; i<n; i++)  {
			sum += cin[i];
	}
    return (int)(sum % 1000000007);
}

static PyObject *np_modsum(PyObject *self, PyObject *args)
{
	PyArrayObject *vecin;  // The python objects to be extracted from the args
	                                //   python vectors, cin and cout point to the row
	                                //   of vecin and vecout, respectively
	/* Parse tuples separately since args will differ between C fcns */
	if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &vecin
		))  return NULL;
	if (NULL == vecin)  return NULL;
	/* Check that objects are 'double' type and vectors
	     Not needed if python wrapper function checks before call to this routine */
	if (not_doublevector(vecin)) return NULL;

	/* Change contiguous arrays into C * arrays   */
	uint64_t *cin=pyvector_to_Carrayptrs(vecin);
	/* Get vector dimension. */
	size_t n=vecin->dimensions[0];

	return Py_BuildValue("i", my_modsum(cin, n));
}

/* ==== Square vector components & multiply by a float =========================
/* #### Vector Utility functions ######################### */

/* ==== Make a Python Array Obj. from a PyObject, ================
     generates a double vector w/ contiguous memory which may be a new allocation if
     the original was not a double type or contiguous
  !! Must DECREF the object returned from this routine unless it is returned to the
     caller of this routines caller using return PyArray_Return(obj) or
     PyArray_BuildValue with the "N" construct   !!!
*/
PyArrayObject *pyvector(PyObject *objin)  {
	return (PyArrayObject *) PyArray_ContiguousFromObject(objin,
		NPY_DOUBLE, 1,1);
}
/* ==== Check that PyArrayObject is a double (Float) type and a vector ==============
    return 1 if an error and raise exception */
int  not_doublevector(PyArrayObject *vec)  {
	if (vec->descr->type_num != NPY_UINT64 || vec->nd != 1)  {
		PyErr_SetString(PyExc_ValueError,
			"In not_doublevector: array must be of type uint644 and 1 dimensional (n).");
		return 1;  }
	return 0;
}

/* #### Matrix Extensions ############################## */

