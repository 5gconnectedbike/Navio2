import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help = "Chose A or B")

    if (len(sys.argv) == 1):
        print("Sys.argv ==1")
        parser.print_help()
        sys.exit(1)
    elif (len(sys.argv) ==2):
        sys.exit("Sys.argv ==2")

    args = parser.parse_args()

    