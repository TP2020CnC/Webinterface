#
# Name: Tester.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-19
# Letzte Änderung: 2020-05-26
#
from multiprocessing import Process
import time
import sys
import random
try:
    from Webinterface.library.KartenUpdater import KartenUpdater
except:
    from KartenUpdater import KartenUpdater


def worker(num):
    """thread worker function"""
    ku = KartenUpdater("C:/test/")
    ku.Update()
    sys.stdout.flush()
    return


def main():
    jobs = []
    t1 = Process(target=worker, args=(1,))
    t1.start()
    while 1:
        pass


if __name__ == '__main__':
    main()
