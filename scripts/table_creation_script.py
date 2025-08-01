import re
import pandas as pd
import pdfplumber
import camelot
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

# Path to the PDF file
PDF_PATH = "submission_2/2025SUStats_womens_lacrosse.pdf"
# Optional: specify path to poppler if not in PATH
POPLER_PATH = "/opt/homebrew/bin"


def extract_record_summary(pdf_path: str) -> pd.DataFrame:
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()

    pattern = re.compile(
        r"^(ALL GAMES|CONFERENCE|NON-CONFERENCE)\s+"
        r"(\d+-\d+)\s+"
        r"(\d+-\d+)\s+"
        r"(\d+-\d+)\s+"
        r"(\d+-\d+)",
        re.MULTILINE
    )
    records = []
    for line in text.split("\n"):
        m = pattern.match(line.strip())
        if m:
            type_, overall, home, away, neutral = m.groups()
            records.append({
                "Type": type_.title(),
                "Overall": overall,
                "Home": home,
                "Away": away,
                "Neutral": neutral,
            })
    return pd.DataFrame(records)


def parse_game_table(pdf_path: str, year: str) -> pd.DataFrame:
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
    lines = text.split("\n")

    header_idx = next(
        (i for i, l in enumerate(lines)
         if l.strip().startswith("Date") and "Opponent" in l and "Score" in l and "Att." in l),
        None
    )
    if header_idx is None:
        raise ValueError("Game table header not found")

    rows = []
    for line in lines[header_idx+1:]:
        if not line.strip() or line.strip().startswith("PLAYER") or line.strip().startswith("TEAM STATISTICS"):
            break
        parts = line.split()
        if len(parts) < 4:
            continue
        date = " ".join(parts[0:2]) + f" {year}"
        score = f"{parts[-3]} {parts[-2]}"
        att = int(parts[-1])
        opponent = " ".join(parts[2:-3])
        rows.append({"Date": date, "Opponent": opponent, "Score": score, "Att": att})
    return pd.DataFrame(rows)


def parse_player_table_from_image(pdf_path: str) -> pd.DataFrame:
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPLER_PATH)
    for img in images:
        text = pytesseract.image_to_string(img)
        if "PLAYER" in text and "GP" in text and "Pts" in text:
            lines = text.split("\n")
            break
    else:
        raise ValueError("No page contained the player stats image.")

    records = []
    cols = ["Player", "GP", "G", "A", "Pts", "Sh", "Gw", "GB", "DC", "TO", "CT"]
    for line in lines:
        if not line.strip() or line.strip().startswith("Total") or line.strip().startswith("Opponents"):
            continue
        parts = line.strip().split()
        if len(parts) >= 12:
            name = " ".join(parts[:-11])
            nums = parts[-11:]
            rec = {"Player": name, "GP": nums[0]}
            for i, col in enumerate(cols[2:]):
                rec[col] = nums[i+1]
            records.append(rec)
    return pd.DataFrame(records)


def find_table_by_header(tables, keyword: str):
    for table in tables:
        df = table.df.astype(str)
        header_cells = df.iloc[:2].values.flatten()
        if any(keyword.lower() in cell.lower() for cell in header_cells):
            return table
        temp = df.copy()
        temp.columns = temp.iloc[0]
        if any(keyword.lower() in str(col).lower() for col in temp.columns):
            return table
    return None


def parse_team_stats_from_image(pdf_path: str) -> pd.DataFrame:
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPLER_PATH)
    for img in images:
        text = pytesseract.image_to_string(img)
        if "TEAM STATISTICS" in text:
            lines = text.split("\n")
            break
    else:
        raise ValueError("No page contained the team statistics image.")

    records = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) >= 3:
            label = " ".join(parts[:-2])
            su, opp = parts[-2:]
            records.append({"TEAM STATISTICS": label, "SU": su, "OPP": opp})
    return pd.DataFrame(records)


def parse_period_stats(tables) -> pd.DataFrame:
    stats = ["Goals by Period", "Shots by Period", "Shots on Goal"]  # exclude missing "Saves"
    all_rows = []
    for stat in stats:
        table = find_table_by_header(tables, stat)
        if table is None:
            print(f"Warning: Table not found for '{stat}' — skipping.")
            continue
        df = table.df.copy()
        df.columns = df.iloc[1]
        df = df.drop(index=[0,1]).reset_index(drop=True)
        if df.columns[0] != "Team":
            df = df.rename(columns={df.columns[0]: "Team"})
        if "Team" not in df.columns:
            print(f"Skipping malformed table: {stat}")
            continue
        df = df.loc[:, ~df.columns.duplicated()]
        melted = pd.melt(df, id_vars=["Team"], var_name="Period", value_name="Value")
        melted["Statistic"] = stat.replace(" by Period", "")
        all_rows.append(melted)
    return pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()


if __name__ == "__main__":
    year_match = re.search(r"(\d{4})", PDF_PATH)
    year = year_match.group(1) if year_match else ""

    record_df = extract_record_summary(PDF_PATH)
    record_df.to_csv("record_summary.csv", index=False)

    game_df = parse_game_table(PDF_PATH, year)
    game_df.to_csv("game_stats.csv", index=False)

    player_df = parse_player_table_from_image(PDF_PATH)
    player_df.to_csv("player_stats.csv", index=False)

    team_df = parse_team_stats_from_image(PDF_PATH)
    team_df.to_csv("team_stats.csv", index=False)

    tables = camelot.read_pdf(PDF_PATH, pages="1-end", flavor="stream")
    period_df = parse_period_stats(tables)
    period_df.to_csv("period_stats.csv", index=False)

    print("Extraction complete: record, game, player, team, and period CSVs.")
