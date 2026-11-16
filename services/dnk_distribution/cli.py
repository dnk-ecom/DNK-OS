import sys
from services.dnk_distribution.src.service import process_data

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "default"
    print(process_data(query))
