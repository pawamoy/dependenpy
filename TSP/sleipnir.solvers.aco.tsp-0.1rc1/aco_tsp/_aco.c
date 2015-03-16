/*  -*- mode: C; c-basic-offset: 4; coding: utf-8 -*-
 *
 *  aco.c: C optimizations for TSP ACO algorithm
 *
 *  Copyright 2011 Carlos Martín
 *  Copyright 2011 Universidad de Salamanca
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License 2.1 as published by the Free Software Foundation.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 * USA
 */

#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef STDC_HEADERS
# include <stddef.h>
#else /* !STDC_HEADERS */
# ifdef HAVE_SYS_TYPES_H
#  include <sys/types.h> /* For size_t */
# endif /* HAVE_SYS_TYPES_H */
#endif /* !STDC_HEADERS */

#include <assert.h>
#include <time.h>

#ifndef UNUSED
# define UNUSED __attribute__((unused))
#endif


/*
KISS pseudorandom generator

copyright: Copyright (c) 2004 Kris Bell. All rights reserved
license: BSD style: $(LICENSE)
version: Initial release: April 2004
author: various
From: Tango

KISS (via George Marsaglia & Paul Hsieh)

the idea is to use simple, fast, individually promising
generators to get a composite that will be fast, easy to code
have a very long period and pass all the tests put to it.
The three components of KISS are

    x(n)=a*x(n-1)+1 mod 2^32
    y(n)=y(n-1)(I+L^13)(I+R^17)(I+L^5),
    z(n)=2*z(n-1)+z(n-2) +carry mod 2^32

The y's are a shift register sequence on 32bit binary vectors
period 2^32-1; The z's are a simple multiply-with-carry sequence
with period 2^63+2^32-1.

The period of KISS is thus 2^32*(2^32-1)*(2^63+2^32-1) > 2^127
*/


static unsigned int kiss_x = 1;
static unsigned int kiss_y = 2;
static unsigned int kiss_z = 4;
static unsigned int kiss_w = 8;
static unsigned int kiss_carry = 0;
static unsigned int kiss_k = 0;
static unsigned int kiss_m = 0;

static void
_fast_seed(unsigned int seed) {
    kiss_x = seed | 1;
    kiss_y = seed | 2;
    kiss_z = seed | 4;
    kiss_w = seed | 8;
    kiss_carry = 0;
}

static unsigned int 
fast_rand_uint(void) {
    kiss_x = kiss_x * 69069 + 1;
    kiss_y ^= kiss_y << 13;
    kiss_y ^= kiss_y >> 17;
    kiss_y ^= kiss_y << 5;
    kiss_k = (kiss_z >> 2) + (kiss_w >> 3) + (kiss_carry >> 2);
    kiss_m = kiss_w + kiss_w + kiss_z + kiss_carry;
    kiss_z = kiss_w;
    kiss_w = kiss_m;
    kiss_carry = kiss_k >> 30;
    return kiss_x + kiss_y + kiss_w;
}

static double 
fast_random(void) {
    return fast_rand_uint() / (UINT_MAX + 1.0);
}

static int 
fast_rand_int(int max) {
    int k, n;
    n = max + 1;
    k = (int)(n * (fast_rand_uint() / (UINT_MAX + 1.0)));
    return (k == n) ? k - 1 : k;
}


PyDoc_STRVAR(fast_seed__doc__,
    "fast_seed(a=None)\n\n"
    "Initialize internal state from hashable object.\n\n"
    "None or no argument seeds from current time or from \n"
    "an operating system specific randomness source if available.\n\n"
    "If a is not None or an int or long, hash(a) is used instead.\n"
);

static PyObject *
fast_seed(PyObject *unused UNUSED, PyObject *args)
{
    PyObject *dcls = NULL;
    PyObject *hash;
    long long_hash;
    static PyObject *seed = NULL;
    time_t now;

    if (! PyArg_ParseTuple(args, "O:fast_seed", &hash)) {
        return NULL;
    }
    if ((long_hash = PyObject_Hash(hash)) < 0) {
        time(&now);
        long_hash = (long)now;
    }

#define PEEK_METHOD(dcls, name) PyObject_GetAttrString(dcls, # name)
    if (seed == NULL) {
        if (! (dcls = PyImport_ImportModule("random"))) {
            return NULL;
        }
        if (! (seed = PEEK_METHOD(dcls, seed))) {
            Py_DECREF(dcls);
            return NULL;
        }
#undef PEEK_METHOD
    }

    /* prepare hashable to passe to seeders */
    hash = PyLong_FromLong(long_hash);

    /* finally, init seeds */
    PyObject_CallFunctionObjArgs(seed, hash, NULL);
    _fast_seed(long_hash);
    
    Py_XDECREF(dcls);
    Py_DECREF(hash);
    
    Py_RETURN_NONE;
}




struct _methods {
    int initiated;
    PyObject *sum_weights;
    PyObject *find_sum_weights;
    PyObject *evaporate_pherom;
};

static struct _methods _methods = {
    .initiated = 0,
    .sum_weights = NULL,
    .find_sum_weights = NULL,
    .evaporate_pherom = NULL,
};

static int
_import() {

    PyObject *dcls;

#define IMPORT_ARGS         PyEval_GetGlobals(), PyEval_GetLocals()
#define PEEK_METHOD(dcls, name) PyObject_GetAttrString(dcls, # name)
#define RETURN_IMPORT_ERROR Py_XDECREF(dcls); return -1

    if (! (dcls = PyImport_ImportModuleLevel("ants", IMPORT_ARGS, NULL, 1))) {
        RETURN_IMPORT_ERROR;
    }
    if (! (_methods.sum_weights = PEEK_METHOD(dcls, sum_weights))) {
        RETURN_IMPORT_ERROR;
    }
    if (! (_methods.find_sum_weights = PEEK_METHOD(dcls, find_sum_weights))) {
        RETURN_IMPORT_ERROR;
    }
    if (! (_methods.evaporate_pherom = PEEK_METHOD(dcls, evaporate_pherom))) {
        RETURN_IMPORT_ERROR;
    }

#undef RETURN_IMPORT_ERROR
#undef PEEK_METHOD
#undef IMPORT_ARGS

    _methods.initiated = 1;
    Py_DECREF(dcls);

    return 0;
}

#define DEFINE_STRING(S) \
    static PyObject *s## S;

#define IMPORT_STRING(S) \
    if(! (s ## S = PyUnicode_FromString(# S))) return NULL

#define METHOD_ENTRY(name,flags) {#name, (PyCFunction)name, flags, name##__doc__}

/* PyObject Method Declarations */
PyDoc_STRVAR(sum_weights__doc__,
    "sum_weights(locs, size, pherom, user, current)\n\n"
    "Sum weights for all paths to locations adjacent\n"
    "to current one, balanced with pheromone state.\n"
);

static inline float
_sum_weights(PyObject *restrict locs, int locs_size,
             PyObject *restrict pher, PyObject *restrict used, int cur)
{
    /* iterator */
    int i;

    /* Store locs and phers tuples for current */
    PyObject *clocs;
    PyObject *cpher;

    /* Store partial results */
    float rtotal0 = 0.0f;
    float rtotal1 = 0.0f;
    float rtotal2 = 0.0f;
    float rtotal3 = 0.0f;

    /* Peek tuples */
    assert(!(locs_size % 4));
    clocs = PyList_GET_ITEM(locs, cur);
    cpher = PyList_GET_ITEM(pher, cur);

    /* Now iterate over all elements of tuple/pher */
    for (i = 0; i < (locs_size/4)*4; i+=4) {
#define PEEK_FT(frm ,ind) (float)PyFloat_AS_DOUBLE(PyList_GET_ITEM(frm, ind))
#define PEEK_LT(frm, ind) (long)PyInt_AS_LONG(PyList_GET_ITEM(frm, ind))

        rtotal0 += PEEK_FT(clocs, i)   * (1.0f + PEEK_FT(cpher, i))   * (! PEEK_LT(used, i));
        rtotal1 += PEEK_FT(clocs, i+1) * (1.0f + PEEK_FT(cpher, i+1)) * (! PEEK_LT(used, i+1));
        rtotal2 += PEEK_FT(clocs, i+2) * (1.0f + PEEK_FT(cpher, i+2)) * (! PEEK_LT(used, i+2));
        rtotal3 += PEEK_FT(clocs, i+3) * (1.0f + PEEK_FT(cpher, i+3)) * (! PEEK_LT(used, i+3));

#undef PEEK_FT
#undef PEEK_LT
    }
    return rtotal0 + rtotal1 + rtotal2 + rtotal3;
}

static PyObject *
sum_weights(PyObject *unused UNUSED, PyObject *args)
{
    PyObject *locs, *pherom, *used;
    int size, current;

    if (!PyArg_ParseTuple(
            args,
            "OiOOi:sum_weights",
            &locs, &size, &pherom, &used, &current)) {
        return NULL;
    }

    return PyFloat_FromDouble(  \
        _sum_weights(locs, size, pherom, used, current));
}

/*----*/
PyDoc_STRVAR(find_sum_weights__doc__,
    "find_sum_weights(locs, size, pherom, used, current, sought)\n\n"
    "Returns a location ant sought.\n"
);

static inline long
_find_sum_weights(PyObject *restrict locs, int locs_size,
                  PyObject *restrict pher, PyObject *restrict used,
                  int cur, PyObject *restrict sought)
{
    /* iterator */
    long i;
    long next = 0;

    /* Store locs and phers tuples for current */
    PyObject *clocs;
    PyObject *cpher;

    /* Store partial results */
    float rtotal0 = 0.0f;

    /* sought */
    float rsought0 = (float)PyFloat_AS_DOUBLE(sought);

    /* Peek tuples */
    clocs = PyList_GET_ITEM(locs, cur);
    cpher = PyList_GET_ITEM(pher, cur);

    /* Now iterate over all elements of tuple/pher */
    for (i = 0; i < locs_size; i++) {
        if (rtotal0 >= rsought0) {
            break;
        }
#define PEEK_FT(frm ,ind) (float)PyFloat_AS_DOUBLE(PyList_GET_ITEM(frm, ind))
        if (! PyInt_AS_LONG(PyList_GET_ITEM(used, i))) {
            rtotal0 += PEEK_FT(clocs, i) * (1.0f + PEEK_FT(cpher, i));
            next = i;
        }
#undef PEEK_FT
    }
    return next;
}

static PyObject *
find_sum_weights(PyObject *unused UNUSED, PyObject *args)
{
    PyObject *locs, *pherom, *used, *sought;
    int size, current;

    if (!PyArg_ParseTuple(
            args,
            "OiOOiO:sum_weights",
            &locs, &size, &pherom, &used, &current, &sought)) {
        return NULL;
    }

    return PyInt_FromLong(                                             \
        _find_sum_weights(locs, size, pherom, used, current, sought));
}


PyDoc_STRVAR(evaporate_pherom__doc__,
    "evaporate_pherom(pher, max_iter, boost)\n\n"
    "Evaporates pheromone after after an ant route.\n"
);


static inline void
_evaporate_pherom(PyObject *restrict pher, int locs_size, int miter, int boost)
{
    /* iterators */
    int row, col;

    /* Store locs and phers tuples for current */
    PyObject *tuple;
    float value = 0.0f;

    /* pherom decrease value */
    float decr = (float) boost / miter;

    /* Now iterate over all elements of tuple/pher */
    for (row = 0; row < locs_size; row++) {
        tuple = PyList_GET_ITEM(pher, row);
        for (col = 0; col < locs_size; col++) {
            value = (float)PyFloat_AS_DOUBLE(PyList_GET_ITEM(tuple, col));
            if (value) {
                PyList_SetItem(                                         \
                    tuple, col, PyFloat_FromDouble(                     \
                        (value > decr) * (value - decr)));
            }
        }
    }
}

static PyObject *
evaporate_pherom(PyObject *unused UNUSED, PyObject *args)
{
    PyObject *pher;
    int boost;
    int miters;
    int size;

    if (!PyArg_ParseTuple(
            args,
            "Oiii:evaporate_pherom",
            &pher, &size, &miters, &boost)) {
        return NULL;
    }

    _evaporate_pherom(pher, size, miters, boost);

    Py_RETURN_NONE;
}

PyDoc_STRVAR(gen_path__doc__,
    "gen_path(locs, size, pher)\n\n"
    "Generate a random route for all locs based on its weight\n\n"
    "and pher state.\n"
);

static inline PyObject *
_gen_path(PyObject *restrict locs, int locs_size, PyObject *restrict pher)
{
    /* iterators */
    int i, curr;
    int pos_path, nused;

    /* Store locs and phers tuples for current */
    PyObject *path, *used;
    PyObject *size, *zero, *one;

    /* peek a random city */
    curr = fast_rand_int(locs_size - 1);
    size = PyInt_FromLong(locs_size);

    /* create empty path */
    path = PyList_New(locs_size);
    PyList_SET_ITEM(path, 0, PyInt_FromLong(curr));
    pos_path = 1;

    /* create used list */
    used = PyList_New(locs_size);
    zero = PyInt_FromLong(0);
    for (i = 0; i < locs_size; i++) {
        Py_INCREF(zero);
        PyList_SET_ITEM(used, i, zero);
    }
    Py_DECREF(zero);

    /* mark as used */
    one  = PyInt_FromLong(1);
    PyList_SetItem(used, curr, one);
    nused = 1;

    while (nused < locs_size) {

#define CALL PyObject_CallFunctionObjArgs

        PyObject *sweight, *current, *rnd, *nxt;
        /* calculate sums */
        current = PyInt_FromLong(curr);

        sweight = CALL(_methods.sum_weights, locs, size, pher, used, current, NULL);
        rnd = PyFloat_FromDouble(fast_random() * (float)PyFloat_AS_DOUBLE(sweight));
        nxt = CALL(_methods.find_sum_weights, locs, size, pher, used, current, rnd, NULL);

        Py_DECREF(current);
        Py_DECREF(rnd);

        PyList_SET_ITEM(path, pos_path++, nxt);
        curr = PyInt_AS_LONG(nxt);

        if (PyList_GET_ITEM(used, curr) != one) {
            nused ++;
            Py_INCREF(one);
            PyList_SetItem(used, curr, one);
        }
#undef CALL
    }

    Py_DECREF(size);
    Py_DECREF(used);

    return path;
}

static PyObject *
gen_path(PyObject *unused UNUSED, PyObject *args)
{
    PyObject *locs, *pher;
    int size;

    if (! _methods.initiated && _import() < 0) {
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "OiO:gen_path", &locs, &size, &pher)) {
        return NULL;
    }
    return _gen_path(locs, size, pher);
}

/* PyObject Module */
static PyMethodDef module_funcs[] = {
    METHOD_ENTRY(evaporate_pherom, METH_VARARGS),
    METHOD_ENTRY(find_sum_weights, METH_VARARGS),
    METHOD_ENTRY(gen_path, METH_VARARGS),
    METHOD_ENTRY(fast_seed, METH_VARARGS),
    METHOD_ENTRY(sum_weights, METH_VARARGS),
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_docs,
    "C optimizations for Ant Colony Optimzations heuristic -\n"
    "This module is used internally by AcoTSP solver. Don't use this`\n"
    "module directly.\n"
);

PyMODINIT_FUNC
init_aco(void) {

    PyObject *self;

    if (!(self = Py_InitModule3("_aco", module_funcs, module_docs))) {
        return;
    }
}
