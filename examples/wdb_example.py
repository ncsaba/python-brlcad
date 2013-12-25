"""
This is the python version of wdb_example.c using the python-brlcad module.

usage:

    python wdb_example.py output.g

    # want to render to file?
    rtedge -s 1024 -F output.pix output.g box_n_ball.r
    pix-png -s 1024 < output.pix > output.png

wdb_example.c header text:

    Create a BRL-CAD geometry database from C code.

    Note that this is for writing (creating/appending) a database.

    Note that since the values in the database are stored in millimeters, the
    arguments to the mk_* routines are constrained to also be in millimeters.

python attribution:

    :author: Bryan Bishop <kanzure@gmail.com>
    :date: 2013-09-09
    :license: BSD
"""

# sys has argv
import sys

# there are some rough spots, sorry
import ctypes

import brlcad._bindings.libwdb as wdb
import brlcad._bindings.librt as rt

def main(argv):
    """
    Try to be as similar to the original C source code as possible. There's a
    lot of python sugar and python magic that isn't being invoked here.
    """
    # TODO: support native python lists
    p1 = (ctypes.c_double * 3)()
    p2 = (ctypes.c_double * 3)()
    rgb = (ctypes.c_double * 3)()

    # wdb_fopen isn't in libwdb. It's actually exported in "raytrace.h" which
    # is made available through librt.
    db_fp = rt.wdb_fopen(argv[1])

    # create the database header record
    wdb.mk_id(db_fp, "My Database")

    # All units in the database file are stored in millimeters. This constrains
    # the arguments to the mk_* routines to also be in millimeters.

    # make a sphere centered at 1.0, 2.0, 3.0 with radius 0.75
    p1[:] = [1.0, 2.0, 3.0]
    wdb.mk_sph(db_fp, "ball.s", p1, 0.75)

    # Make an rpp under the sphere (partly overlapping). Note that this realy
    # makes an arb8, but gives us a shortcut for specifying the parameters.
    p1[:] = [0, 0, 0]
    p2[:] = [2, 4, 2.5]
    wdb.mk_rpp(db_fp, "box.s", p1, p2)

    # Make a region that is the union of these two objects. To accomplish
    # this, we need to create a linked list of the items that make up the
    # combination. The wm_hd structure serves as the head of the list of items.

    wm_hd = wdb.wmember()

    somelistp = wdb.bu_list_new()
    wdb.mk_pipe_init(somelistp) # calls BU_LIST_INIT(headp)
    somelistp.contents.magic = 0x01016580 # BU_LIST_HEAD_MAGIC

    # TODO: figure out why the call to mk_addmember will otherwise fail. And
    # why is ctypes telling me that None is not something that can be passed?
    nonestuff = None
    wdb._libs.values()[0].mk_addmember.argtypes = [wdb.String, ctypes.POINTER(wdb.struct_bu_list), ctypes.c_voidp, ctypes.c_int]

    # Create a wmember structure for each of the items that we want in the
    # combination. The return from mk_addmember is a pointer to the wmember
    # structure.
    some_wmember = wdb._libs['/home/csaba/deploy/brlcad/dev-7.24.1/lib/libwdb.so'].mk_addmember("box.s", somelistp, nonestuff, ord("u"))

    # Add the second member to the database.
    #
    # Note that there is nothing which checks to make sure that "ball.s" exists
    # in the database when you create the wmember structure OR when you create
    # the combination. So mis-typing the name of a sub-element for a
    # region/combination can be a problem.
    another_wmember = wdb._libs['/home/csaba/deploy/brlcad/dev-7.24.1/lib/libwdb.so'].mk_addmember("ball.s", somelistp, nonestuff, ord("u"))

    # Create the combination
    #
    # In this case we are going to make it a region (hence the is_region flag
    # is set), and we provide shader parameter information.
    #
    # When making a combination that is NOT a region, the region flag argument
    # is 0, and the strings for optical shader, and shader parameters should
    # (in general) be null pointers.
    is_region = 1

    rgb[:] = [64, 180, 96] # a nice green

    wdb.mk_comb(
        db_fp,
        "box_n_ball.r", # name of the db element created
        somelistp, # list of elements and boolean operations
        is_region, # flag: this is a region
        "plastic", # optical shader
        "di=.8 sp=.2", # shader parameters
        rgb, # item color
        0, 0, 0,
        0, 0, 0,
        0)

    wdb.make_hole(db_fp, p1, p2, 0.75, 0, 0)

    rt.wdb_close(db_fp)

if __name__ == "__main__":
    main(sys.argv)
