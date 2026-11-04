import pandas as pd
import matplotlib.pyplot as plt

'''
STEP 1: Load CSV (Data File)
'''
data_file = 'data/raw/stack_overflow_data.csv'
df = pd.read_csv(data_file)
# print(df.head())

'''
STEP 2: Data Inspection
.shape - dimension size
.info() - structure
.isna().sum() - Missing values
.duplicated(...).sum() - count repeated keys
'''
# print(f"Shape: {df.shape}\n")
# print(df.info())
# print("\n")
# print(f"Missing Values: {df.isna().sum()}\n")
# print(f"Duplicate year-tag pairs: {df.duplicated(["year", "tag"]).sum()}\n")

'''
STEP 3: Percentage of questions that had the 'r' tag in 2020?
'''
r_2020 = df[(df['tag'] == "r") & (df['year'] == 2020)]
print(f" Percentage of questions with 'r' tag in 2020: {(r_2020["num_questions"]/r_2020["year_total"]).values[0]*100}")

'''
STEP 4: Five tags receiving the most questions during 2015–2020?
'''
recent_data = df[df["year"].between(2015, 2020)]
top_five = recent_data.groupby("tag")["num_questions"].sum().sort_values(ascending=False).head(5)
top_five.rename("total_questions").to_csv(
    "results/ top_five_tag_trends.csv"
)

print(f" Five tags with most questions during 2015-2020: {top_five}")

'''
STEP 5: Calculate the yearly question shares for those top five tags.
'''
top_tag_data = df[df['tag'].isin(top_five.index)].copy()
top_tag_data["question_share_pctg"] = (top_tag_data["num_questions"] / top_tag_data["year_total"] * 100)
top_tag_data = top_tag_data.sort_values(["tag", "year"])
top_tag_data.to_csv(
    "results/yearly_tag_shares.csv"
)
# print (top_tag_data.head(10))

'''
Step 6: Plot the distribution
'''
fig, ax = plt.subplots(figsize=(10, 6))
for tag, group in top_tag_data.groupby("tag"):
    ax.plot(
        group["year"],
        group["question_share_pctg"],
        label=tag
    )

ax.set_title("Stack Overflow Question Shares, 2008–2020\nTop 5 Tags by Question Count in 2015–2020")
ax.set_xlabel("Year")
ax.set_ylabel("Questions carrying tag (%)")
ax.legend(title="Tag")
ax.grid(alpha=0.3)
fig.tight_layout()

fig.savefig("results/top_five_tag_trends.png", dpi=300)
plt.show()
