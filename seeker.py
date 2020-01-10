#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import time
import os
import sys

class Seeker():
    # 初期化。
    # Linuxコマンドのワイルドカード使用。正規表現は多分不可。
    def __init__(self, filepath):
        self.__path = filepath
        # ポジション保持用dict.
        # inodeをキーとする.
        self.__seek_pos = dict() 
        # 現在のファイルサイズでseekposを初期化。
        for path in glob.glob(filepath):
            inode = os.stat(path).st_ino
            size = os.path.getsize(path)
            self.__seek_pos[inode] = dict()
            self.__seek_pos[inode]['pos'] = size
            self.__seek_pos[inode]['path'] = path

    def get_all_pos(self):
        return self.__seek_pos

    # ファイル一覧を更新。
    def refresh(self):
        for path in glob.glob(self.__path):
            inode = os.stat(path).st_ino
            # 新しいinodeのファイルがある時
            if inode not in self.__seek_pos:
                inode = os.stat(path).st_ino
                self.__seek_pos[inode] = dict()
                self.__seek_pos[inode]['pos'] = 0
                self.__seek_pos[inode]['path'] = path
                continue
            # ファイル名が変更されたとき
            if self.__seek_pos[inode]['path'] != path:
                self.__seek_pos[inode]['path'] = path

    # 全ファイルで、pos以降にある行をすべて読み込み(ソートなし)。
    def read_all(self):
        self.refresh()
        result = []
        for inode in self.__seek_pos.keys():
            path = self.__seek_pos[inode]['path']
            res, nextpos = self.__read(path, self.__seek_pos[inode]['pos'])
            result.extend(res)
            # 現在のseekposを更新
            self.__seek_pos[inode]['pos'] = nextpos

        return result

    # pathのファイルのseekpos以降をreadlinesするfunc.
    def __read(self, path, seekpos):
        size = os.path.getsize(path)
        # seekposがファイルサイズと同一の場合何もなし。
        if seekpos == size:
            return [], seekpos
        # seekposがファイルサイズより大きい場合、ローテーションされたと判断する。
        # seekposを0に戻す。
        if seekpos > size:
            seekpos = 0 

        # seekpos以降の行を読み込み。
        with open(path, 'rb+') as f:
            f.seek(seekpos,0)
            lines = f.readlines()
            nextpos = f.tell()
        
        return lines, nextpos

if __name__ == '__main__':
    seeker = Seeker(sys.argv[1])

    while True:
        result = seeker.read_all()
        for l in result:
            print(l.rstrip())
        time.sleep(1)