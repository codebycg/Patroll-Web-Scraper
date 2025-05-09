import openpyxl

def simulated_patent_search(base_patent: str, winning_patents: list, prior_art_list: list):
    winning_set = set(p.upper() for p in winning_patents)
    found_set = set(p.upper() for p in prior_art_list)
    found_matches = list(winning_set & found_set)
    success = len(found_matches) > 0
    return found_matches, success

# Load workbook
excel_path = "PatentPlusAI Week 2 Deliverable.xlsx"
wb = openpyxl.load_workbook(excel_path)
sheet = wb["Scraped Contests"]

# Define mock ground truth prior art
# 🛠️ Replace this with real known answers if you have them!
# For now, using a simple dictionary
ground_truth = {
    "US1234567B2": ["US7654321B1", "US9999999A1"],
    "US2468135B2": ["US1357924A1", "US9876543B2"],
    # Add more if known
}

# Initialize metrics
total = 0
success_count = 0
precision_scores = []
recall_scores = []

for row in sheet.iter_rows(min_row=2, values_only=True):
    troll_patent, prior_art_str, _, _, _ = row
    if not troll_patent or troll_patent not in ground_truth:
        continue  # Skip rows without known ground truth

    scraped_prior_art = [pat.strip().upper() for pat in prior_art_str.split(",") if pat.strip()]
    correct_prior_art = [p.upper() for p in ground_truth[troll_patent]]

    found, success = simulated_patent_search(troll_patent, correct_prior_art, scraped_prior_art)

    # Calculate precision and recall
    true_positives = len(found)
    precision = true_positives / len(scraped_prior_art) if scraped_prior_art else 0
    recall = true_positives / len(correct_prior_art) if correct_prior_art else 0

    precision_scores.append(precision)
    recall_scores.append(recall)

    if success:
        success_count += 1
    total += 1

# Compute final metrics
accuracy = (success_count / total) * 100 if total else 0
mean_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
mean_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0

print(f"\n Evaluation Metrics:")
print(f"Total Contests Evaluated: {total}")
print(f"Success Rate: {accuracy:.2f}%")
print(f"Average Precision: {mean_precision:.2f}")
print(f"Average Recall: {mean_recall:.2f}")
