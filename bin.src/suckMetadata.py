#!/usr/bin/env python

import os
from glob import glob
import sqlite3
from argparse import ArgumentParser
from lsst.afw.image import readMetadata

def extractor(keyword, valueType=str):
    return lambda md: valueType(md.get(keyword))

def sexagesimal(keyword, multiplier=1.0):
    def translator(md):
        sex = md.get(keyword)
        if sex[0] in "+-":
            sign = -1 if sex[0] == "-" else +1
            sex = sex[1:]
        else:
            sign = +1
        dd, mm, ss = map(float, sex.split(":"))
        return sign*(dd + mm/60.0 + ss/3600.0)*multiplier
    return translator

SHUTTER = {
    "date": ('TEXT', lambda md: md.get("DATE-OBS") + "T" + md.get("UTC")),
    "object": ('TEXT', extractor("OBJECT")),
    "type": ('TEXT', extractor("IMAGETYP")),
    "filter": ('TEXT', extractor("FILTER")),
    "ra": ('DOUBLE', sexagesimal("RA", 15.0)),
    "decl": ('DOUBLE', sexagesimal("DEC")),
    "expTime": ('DOUBLE', extractor("EXPTIME", float)),
}

CAMERA = {
    "date": ('TEXT', extractor("DATE-OBS")),
    "expTime": ('DOUBLE', extractor("EXPTIME", float)),
}

def getDatabase(root):
    return sqlite3.connect(os.path.join(root, "monocam.sqlite"))

def createTable(conn, table, columns):
    cmd = "CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, " % table
    cmd += ", ".join([("%s %s" % (col, colData[0])) for col, colData in columns.iteritems()])
    cmd += ")"
    conn.execute(cmd)

def createDatabase(root):
    conn = getDatabase(root)
    createTable(conn, "shutter", SHUTTER)
    createTable(conn, "camera", CAMERA)

    # Join table
    #conn.execute("CREATE TABLE match (camera INTEGER PRIMARY KEY, shutter INTEGER PRIMARY KEY)")

    conn.commit()
    conn.close()

def suckMetadata(root, table, columns, filenames):
    conn = getDatabase(root)
    for fn in sum([glob(fn) for fn in filenames], []):
        md = readMetadata(fn, 1)
        try:
            data = {col: colData[1](md) for col, colData in columns.iteritems()}
        except Exception as e:
            print "WARNING: Unable to parse headers from %s: %s" % (fn, e)
            import pdb;pdb.set_trace()
            continue
        sql = "INSERT INTO %s VALUES (NULL, ?" % table
        sql += ", ?" * len(columns)
        sql += ")"
        values = [os.path.abspath(fn)] + [data[col] for col in columns]
        conn.execute(sql, values)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--root", required=True, help="Data repo root")
    sub = parser.add_subparsers()

    sub.add_parser('create', help='create database').set_defaults(
        func=lambda args: createDatabase(args.root)
    )

    cameraParser = sub.add_parser("camera", help="suck camera metadata")
    cameraParser.add_argument("files", nargs="+", help="filenames from which to suck metadata")
    cameraParser.set_defaults(func=lambda args: suckMetadata(args.root, "camera", CAMERA, args.files))

    shutterParser = sub.add_parser("shutter", help="suck shutter metadata")
    shutterParser.add_argument("files", nargs="+", help="filenames from which to suck metadata")
    shutterParser.set_defaults(func=lambda args: suckMetadata(args.root, "shutter", SHUTTER, args.files))

    args = parser.parse_args()
    args.func(args)
