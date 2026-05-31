import json
import os

def export_to_readable_format():
    """Doc q_table.json va the hien duoi dang readable (tuy chon)."""
    file_path = "output/q_table.json"
    if not os.path.exists(file_path):
        print("Khong tim thay q_table.json")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        q_table = json.load(f)
        
    print(f"Da load Q-Table voi {len(q_table)} states.")
    # Code export ra CSV hay gi do co the viet o day neu can.

if __name__ == "__main__":
    export_to_readable_format()
