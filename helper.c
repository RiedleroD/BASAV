#define PY_SSIZE_T_CLEAN
#include <python3.8/Python.h>
#include <python3.8/structmember.h>

//mfederczuk zone
#include <errno.h>
#include <stddef.h>
#include <stdlib.h>

enum { GET_RENDER_BUCK_VECTOR_INIT_CAPACITY = 1024 };

#define GET_RENDER_BUCK_VECTOR_CAPACITY_GROW_FACTOR 1.5

/**
 * Pair of `unsigned long long`.
 */
struct ullint_pair {
	unsigned long long first;
	unsigned long long second;
};

/**
 * A pair of a `unsigned long long` vector and a `ullint_pair` vector.
 *
 * `*_begin` is the location of the first element of the vector.
 * `*_end` is the location one after the last element of the vector.
 * If the vector is empty `*_begin` and `*_end` point towards the same location.
 */
struct ullint_vector__ullint_pair_vector__pair {
	unsigned long long* first_begin;
	unsigned long long* first_end;

	struct ullint_pair* second_begin;
	struct ullint_pair* second_end;
};

/**
 * `items_begin` must be the pointer to the location of the first item.
 * `items_end` must be the pointer to the location one after the last item.
 * If it should be empty, `items_begin` and `items_end` should be pointers to
 * the same location.
 *
 *
 * The members `ullint_vector__ullint_pair_vector__pair::first_begin` and
 * `ullint_vector__ullint_pair_vector__pair::second_begin` of the return value must
 * be manually freed.
 *
 *
 * If the system is out of heap memory,
 * `ullint_vector__ullint_pair_vector__pair::first_begin` will be set to `NULL`
 * and `errno` will be set to `ENOMEM`.
 * Accessing the other members in this case is undefined behaviour.
 *
 * No other errors may occur.
 */
struct ullint_vector__ullint_pair_vector__pair get_render_buck(unsigned long long* items_begin, unsigned long long* items_end) {
	#define _return_err \
		return ((struct ullint_vector__ullint_pair_vector__pair){ \
			.first_begin = NULL \
		})


	unsigned long long* iteml_begin = malloc(sizeof(unsigned long long) * GET_RENDER_BUCK_VECTOR_INIT_CAPACITY);
	if(iteml_begin == NULL) _return_err;

	unsigned long long* iteml_end     = iteml_begin;
	unsigned long long* iteml_cap_end = iteml_begin + GET_RENDER_BUCK_VECTOR_INIT_CAPACITY;


	struct ullint_pair* itemq_begin = malloc(sizeof(struct ullint_pair) * GET_RENDER_BUCK_VECTOR_INIT_CAPACITY);
	if(itemq_begin == NULL) {
		int tmp = errno;
		free(iteml_begin);
		errno = tmp;
		_return_err;
	}

	struct ullint_pair* itemq_end     = itemq_begin;
	struct ullint_pair* itemq_cap_end = itemq_begin + GET_RENDER_BUCK_VECTOR_INIT_CAPACITY;


	unsigned long long sindex = 0;
	unsigned long long bindex = 0;


	const size_t items_size = (items_end - items_begin);
	for(size_t i = 0; i < items_size; ) {
		const unsigned long long sit = items_begin[i];
		++i;

		unsigned long long bit = sit + 1;
		bindex = sindex + 1;

		while(i < items_size && bit == items_begin[i]) {
			++bit;
			++bindex;
			++i;
		}

		if(sit + 1 == bit) {
			if(iteml_end == iteml_cap_end) {
				const size_t old_cap = (iteml_cap_end - iteml_begin);
				const size_t new_cap = old_cap * GET_RENDER_BUCK_VECTOR_CAPACITY_GROW_FACTOR;

				unsigned long long* const tmp = realloc(iteml_begin, sizeof(unsigned long long) * new_cap);
				if(tmp == NULL) {
					int tmperrno = errno;
					free(iteml_begin);
					free(itemq_begin);
					errno = tmperrno;
					_return_err;
				}

				iteml_begin = tmp;
				iteml_end = iteml_begin + old_cap;
				iteml_cap_end = iteml_begin + new_cap;
			}

			(*iteml_end) = sindex;
			++iteml_end;
		} else {
			if(itemq_end == itemq_cap_end) {
				const size_t old_cap = (itemq_cap_end - itemq_begin);
				const size_t new_cap = old_cap * GET_RENDER_BUCK_VECTOR_CAPACITY_GROW_FACTOR;

				struct ullint_pair* const tmp = realloc(itemq_begin, sizeof(struct ullint_pair) * new_cap);
				if(tmp == NULL) {
					int tmperrno = errno;
					free(iteml_begin);
					free(itemq_begin);
					errno = tmperrno;
					_return_err;
				}

				itemq_begin = tmp;
				itemq_end = itemq_begin + old_cap;
				itemq_cap_end = itemq_begin + new_cap;
			}

			(*itemq_end) = (struct ullint_pair){
				.first = sindex,
				.second = bindex
			};
			++itemq_end;
		}

		sindex = bindex;
	}

	errno = 0;
	return (struct ullint_vector__ullint_pair_vector__pair){
		.first_begin = iteml_begin,
		.first_end = iteml_end,

		.second_begin = itemq_begin,
		.second_end = itemq_end
	};

	#undef _return_err
}
//mfederczuk zone end

static PyObject* getrenderbuck(PyObject* self, PyObject* args) {
	PyObject* pytems;
	long mode;
	if(!PyArg_ParseTuple(args, "Ol", &pytems, &mode)) return NULL;

	Py_ssize_t len;
	uint8_t type;
	if(PySet_Check(pytems)){
		type=1;
	}else if(PyList_Check(pytems)){
		type=2;
	}else if(PyTuple_Check(pytems)){
		type=3;
	}else{
		type=0;
	}
	switch(type){
		case 0:
			printf("getrenderbuck only accepts sets, tuples and lists");
			exit(1);
		case 1:
			len=PySet_Size(pytems);
			pytems=PyObject_CallMethod(pytems,"copy",NULL);//copy set so original set is unaffected by pops
			break;
		case 2:
			len=PyList_Size(pytems);
			break;
		case 3:
			len=PyTuple_Size(pytems);
			break;
	}
	if(mode==0){
		unsigned long long items[len];
		switch(type){
			case 1:
				for(Py_ssize_t i = 0; i < len; ++i) {
					items[i] = PyLong_AsUnsignedLongLong(PySet_Pop(pytems));
				}
				break;
			case 2:
				for(Py_ssize_t i = 0; i < len; ++i) {
					items[i] = PyLong_AsUnsignedLongLong(PyList_GetItem(pytems, i));
				}
				break;
			case 3:
				for(Py_ssize_t i = 0; i < len; ++i) {
					items[i] = PyLong_AsUnsignedLongLong(PyTuple_GetItem(pytems, i));
				}
				break;
		}

		const struct ullint_vector__ullint_pair_vector__pair result = get_render_buck(items, items + len);

		if(result.first_begin == NULL) {
			PyErr_NoMemory();
			return NULL;
		}

		unsigned long long* iteml = result.first_begin;
		const size_t lsize = result.first_end - iteml;
		struct ullint_pair* itemq = result.second_begin;
		const size_t qsize = result.second_end - itemq;

		PyObject* const pyteml = PyTuple_New(lsize);
		PyObject* const pytemq = PyTuple_New(qsize);
		size_t i;
		for(i = 0; i < lsize; ++i){
			PyTuple_SetItem(pyteml, i, PyLong_FromUnsignedLongLong(iteml[i]));
		}

		PyObject* tup;
		for(i = 0; i < qsize; ++i){
			tup = PyTuple_New(2);
			PyTuple_SetItem(tup, 0, PyLong_FromUnsignedLongLong(itemq[i].first));
			PyTuple_SetItem(tup, 1, PyLong_FromUnsignedLongLong(itemq[i].second));
			PyTuple_SetItem(pytemq, i, tup);
		}

		tup = PyTuple_New(2);
		PyTuple_SetItem(tup, 0, pyteml);
		PyTuple_SetItem(tup, 1, pytemq);

		free(iteml);
		free(itemq);

		return tup;
	}else if(mode==1){//not converting the set to a c array and back to a tuple is faster here
		if(type!=1){
			printf("input has to be set in mode 1");
			return NULL;
		}
		unsigned long long sact, bact, actl[len];
		struct ullint_pair actq[len];
		Py_ssize_t i,il=0,iq=0;
		for(i=0;i<len;i++){
			sact=PyLong_AsUnsignedLongLong(PySet_Pop(pytems));
			bact=sact+1;
			while(PySet_Discard(pytems,PyLong_FromUnsignedLongLong(sact-1))==1){
				sact--;
				i++;
			}
			while(PySet_Discard(pytems,PyLong_FromUnsignedLongLong(bact))){
				bact++;
				i++;
			}
			if(sact+1==bact){
				actl[il]=sact;
				il++;
			}else{
				actq[iq]=(struct ullint_pair){
					.first=sact,
					.second=bact
					};
				iq++;
			}
		}
		PyObject* tup;
		
		Py_ssize_t qsize=sizeof(actq)/sizeof(struct ullint_pair);
		Py_ssize_t lsize=sizeof(actl)/sizeof(unsigned long long);
		PyObject* pactq=PyTuple_New(qsize);
		for(i = 0; i < qsize; ++i){
			tup = PyTuple_New(2);
			PyTuple_SetItem(tup, 0, PyLong_FromUnsignedLongLong(actq[i].first));
			PyTuple_SetItem(tup, 1, PyLong_FromUnsignedLongLong(actq[i].second));
			PyTuple_SetItem(pactq, i, tup);
		}
		
		PyObject* pactl=PyTuple_New(lsize);
		for(i = 0; i < lsize; ++i){
			PyTuple_SetItem(pactl, i, PyLong_FromUnsignedLongLong(actl[i]));
		}
		
		tup = PyTuple_New(2);
		PyTuple_SetItem(tup, 0, pactl);
		PyTuple_SetItem(tup, 1, pactq);
		
		return tup;
	}else{
		printf("Non-valid mode");
		return NULL;
	}
}


static PyMethodDef HelperMethods[] = {
	{"getrenderbuck", getrenderbuck, METH_VARARGS, "Calculate stuff"},
	{NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef helpermodule = {
	PyModuleDef_HEAD_INIT,
	"helper", // name of module
	NULL,     // module documentation, may be NULL
	-1,       // size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
	HelperMethods
};

PyMODINIT_FUNC PyInit_helper() {
	return PyModule_Create(&helpermodule);
}

int main(int argc, char* argv[]) {
	wchar_t* program = Py_DecodeLocale(argv[0], NULL);
	if (program == NULL) {
		fputs("Fatal error: cannot decode argv[0]\n", stderr);
		return 1;
	}

	// Add a built-in module, before Py_Initialize
	if (PyImport_AppendInittab("helper", PyInit_helper) == -1) {
		fputs("Error: could not extend in-built modules table\n", stderr);
		return 1;
	}

	// Pass argv[0] to the Python interpreter
	Py_SetProgramName(program);

	// Initialize the Python interpreter.  Required.
	// If this step fails, it will be a fatal error.
	Py_Initialize();

	// Optionally import the module; alternatively,
	// import can be deferred until the embedded script
	// imports it.
	if (!PyImport_ImportModule("helper")) {
		PyErr_Print();
		fprintf(stderr, "Error: could not import module 'helper'\n");
	}

	PyMem_RawFree(program);

	return 0;
}
