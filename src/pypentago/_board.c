/*
 * pypentago._board
 * ~~~~~~~~~~~~~~~~
 *
 */


#include "Python.h"
#include "board.h"
#include "ai.h"


static PyObject *CW, *CCW;
static PyObject *SquareNotEmpty;


typedef struct {
    PyObject_HEAD
    struct Board *board;
} BoardObject;

static PyTypeObject BoardType;


signed char get_player_uid(PyObject *player)
{
    long ival;
    PyObject *uid = PyObject_GetAttrString(player, "uid");
    if (uid == NULL)
        return -1;
    else if (!PyInt_Check(uid))
    {
        Py_DECREF(uid);
        PyErr_SetString(PyExc_TypeError, "expected an integer as player.uid");
        return -1;
    }
    ival = PyInt_AsLong(uid);
    Py_DECREF(uid);
    if (ival < 1 || ival > 2)
    {
        PyErr_SetString(PyExc_ValueError, "illegal uid");
        return -1;
    }
    return (signed char)ival;
};


static PyObject *
new_boardobject(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"beginner", NULL};
    char beginner = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|b", kwlist, &beginner))
        return NULL;

    BoardObject *self;
    self = (BoardObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;
    self->board = new_board(beginner);
    return (PyObject *)self;
}


static PyObject *
board_subscript(BoardObject *self, PyObject *key)
{
    signed char row, col;
    if (!PyTuple_Check(key))
    {
        PyErr_SetString(PyExc_TypeError, "key must be a (row, col) tuple");
        return NULL;
    }
    else if (!PyArg_ParseTuple(key, "bb;key must be a (row, col) tuple",
                               &row, &col))
        return NULL;
    else if (row < 0 || row > 5 || col < 0 || col > 5)
    {
        PyErr_SetString(PyExc_ValueError,
                        "value not in range(6)");
        return NULL;
    }

    return PyInt_FromLong(self->board->board[row][col]);
}

#include <stdio.h>
static int
board_ass_subscript(BoardObject *self, PyObject *key, PyObject *value)
{
    signed char row, col;
    long ivalue;
    if (!PyTuple_Check(key))
    {
        PyErr_SetString(PyExc_TypeError, "key must be a (row, col) tuple");
        return -1;
    }
    else if (!PyArg_ParseTuple(key, "bb;key must be a (row, col) tuple",
             &row, &col))
        return -1;
    else if (row < 0 || row > 5 || col < 0 || col > 5)
    {
        PyErr_SetString(PyExc_ValueError,
                        "value not in range(6)");
        return -1;
    }
    else if (!PyInt_Check(value))
    {
        PyErr_SetString(PyExc_ValueError, "value must be an integer");
        return -1;
    }
    ivalue = PyInt_AsLong(value);
    if (ivalue < 0 || ivalue > 2)
    {
        PyErr_SetString(PyExc_ValueError, "value not in range(3)");
        return -1;
    }

    self->board->board[row][col] = (char)ivalue;

    return 0;
}


static PyObject *
board_apply_turn(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"player", "turn", NULL};
    PyObject *player, *turn, *turn_tuple, *rot_dir;
    unsigned char quad, row, col, rot_quad;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO", kwlist, &player,
                                     &turn))
        return NULL;
    turn_tuple = PySequence_Tuple(turn);
    if (turn_tuple == NULL)
        return NULL;
    else if (!PyArg_ParseTuple(turn_tuple, "bbbOb;invalid turn argument", &quad,
                               &row, &col, &rot_dir, &rot_quad))
    {
        Py_DECREF(turn_tuple);
        return NULL;
    }
    Py_DECREF(turn_tuple);

    signed char uid = get_player_uid(player);
    if (uid < 0)
        return NULL;

    if (get_stone(self->board, quad, row, col))
    {
	PyErr_SetNone(SquareNotEmpty);
        return NULL;
    }
    set_value(self->board, quad, row, col, uid);

    int cmp = PyObject_RichCompareBool(rot_dir, CW, Py_EQ);
    if (cmp < 0)
        return NULL;
    else if (cmp)
        rotate_cw(self->board, rot_quad);
    else
    {
        cmp = PyObject_RichCompareBool(rot_dir, CCW, Py_EQ);
        if (cmp < 0)
            return NULL;
        else if (cmp)
            rotate_ccw(self->board, rot_quad);
        else
	{
            PyErr_SetNone(PyExc_ValueError);
            return NULL;
        }
    }

    Py_RETURN_NONE;
}


static PyObject *
board_do_best(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"player", "depth", NULL};
    int depth;
    PyObject *player;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi", kwlist, &player,
                                     &depth))
        return NULL;

    int uid = get_player_uid(player);
    if (uid < 0)
        return NULL;

    self->board->colour = uid;
    struct Turn *turn = find_best(self->board, depth);
    do_turn(self->board, turn);
    free_turn(turn);

    Py_RETURN_NONE;
}



static PyObject *
board_rotate_cw(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"quad", NULL};
    unsigned char quad;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "b", kwlist, &quad))
        return NULL;
    rotate_cw(self->board, quad);
    Py_RETURN_NONE;
}


static PyObject *
board_rotate_ccw(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"quad", NULL};
    unsigned char quad;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "b", kwlist, &quad))
        return NULL;
    rotate_ccw(self->board, quad);
    Py_RETURN_NONE;
}


static PyObject *
board_print(BoardObject *self)
{
    print_board(self->board);
    Py_RETURN_NONE;
}


static PyObject *
board_get_pos(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"quad", "row", "col", NULL};
    unsigned char quad, row, col;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "bbb", kwlist,
                                     &quad, &row, &col))
        return NULL;
    return PyInt_FromLong(get_stone(self->board, quad, row, col));
}


static PyObject *
board_set_pos(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"player", "quad", "row", "col", NULL};
    PyObject *player;
    unsigned char quad, row, col;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Obbb", kwlist, &player,
                                     &quad, &row, &col))
        return NULL;

    signed char uid = get_player_uid(player);
    if (uid < 0)
        return NULL;

    if (get_stone(self->board, quad, row, col))
    {
        PyErr_SetNone(SquareNotEmpty);
        return NULL;
    }

    set_value(self->board, quad, row, col, uid);
    self->board->colour = 3 - uid;

    Py_RETURN_NONE;
}


static PyObject *
board_set_value(BoardObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"value", "quad", "row", "col", NULL};
    unsigned char value, quad, row, col;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "bbbb", kwlist,
                                     &value, &quad, &row, &col))
        return NULL;
    set_value(self->board, quad, row, col, value);
    Py_RETURN_NONE;
}


static PyObject *
board_win(BoardObject *self)
{
    char retval = won(self->board);
    return PyInt_FromLong(retval);
}


static void
boardobject_dealloc(BoardObject *self)
{
    free_board(self->board);
    self->ob_type->tp_free((PyObject *)self);
}


static PyMethodDef board_methods[] = {
    {"apply_turn", (PyCFunction)board_apply_turn, METH_KEYWORDS, ""},
    {"do_best", (PyCFunction)board_do_best, METH_KEYWORDS, ""},
    {"rotate_cw", (PyCFunction)board_rotate_cw, METH_KEYWORDS, ""},
    {"rotate_ccw", (PyCFunction)board_rotate_ccw, METH_KEYWORDS, ""},
    {"_print", (PyCFunction)board_print, METH_NOARGS, ""},
    {"get_pos", (PyCFunction)board_get_pos, METH_KEYWORDS, ""},
    {"set_pos", (PyCFunction)board_set_pos, METH_KEYWORDS, ""},
    {"set_value", (PyCFunction)board_set_value, METH_KEYWORDS, ""},
    {"win", (PyCFunction)board_win, METH_NOARGS, ""},
    {NULL, NULL}
};


static PyMappingMethods board_as_mapping = {
    0,                                  /* mp_length */
    (binaryfunc)board_subscript,        /* mp_subscript */
    (objobjargproc)board_ass_subscript, /* mp_ass_subscript */
};


static PyTypeObject BoardType = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "pypentago._board.Board",           /* tp_name */
    sizeof(BoardObject),                /* tp_basicsize */
    0,                                  /* tp_itemsize */
    /* methods */
    (destructor)boardobject_dealloc,    /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    &board_as_mapping,                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE,                /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    board_methods,                      /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    new_boardobject,                    /* tp_new */
};



static PyMethodDef module_methods[] = {
    {NULL, NULL}
};


PyMODINIT_FUNC
init_board(void)
{
    PyObject *module, *exception_module, *pypentago_module;

    if (PyType_Ready(&BoardType) < 0)
        return;

    module = Py_InitModule("pypentago._board", module_methods);
    if (module == NULL)
        return;

    /* Import `CW` and `CCW` constants */
    pypentago_module = PyImport_ImportModule("pypentago");
    if (pypentago_module == NULL)
        return;
    CW = PyObject_GetAttrString(pypentago_module, "CW");
    if (CW == NULL)
    {
        Py_DECREF(pypentago_module);
        return;
    }
    CCW = PyObject_GetAttrString(pypentago_module, "CCW");
    Py_DECREF(pypentago_module);
    if (CCW == NULL)
        return;

    /* Import the `SquareNotEmpty` exception */
    exception_module = PyImport_ImportModule("pypentago.exceptions");
    if (exception_module == NULL)
        return;

    SquareNotEmpty = PyObject_GetAttrString(exception_module,
                                            "SquareNotEmpty");
    Py_DECREF(exception_module);
    if (SquareNotEmpty == NULL)
        return;

    /* Add BoardType to module */
    Py_INCREF(&BoardType);
    PyModule_AddObject(module, "Board", (PyObject *)&BoardType);
}
