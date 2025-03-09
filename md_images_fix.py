import os
import re

# Define paths
md_file = "/Users/roberthsu/Documents/robertbasement_hugoSite/content/industry_project/Final_test.md"  # Adjust if needed
image_subdir = "industry_project"  # Subdirectory under static/images/
file_name = os.path.splitext(os.path.basename(md_file))[0]
image_dir = f"/images/{image_subdir}/{file_name}_files/"  # Final image path in Hugo

# Read the markdown content
with open(md_file, "r") as f:
    content = f.read()

# test_content = '![png](9tickers_trend_files/9tickers_trend_19_7.png)'
# Replace image paths: `![](your_notebook_files/image1.png)` → `![](/images/some_projs/image1.png)`
updated_content = re.sub(r'!\[(.*?)\]\((.*?_files/)', rf'![\1]({image_dir}', content)
# print(test_content)
# print(updated_content)
# # Write back the modified markdown file
# print(os.path.basename(md_file))

new_md_file = f"content/{image_subdir}/{os.path.basename(md_file)}"
with open(new_md_file, "w") as f:
    f.write(updated_content)

print(f"Updated Markdown saved to {new_md_file}")
print(f"Image paths now point to {image_dir}")
