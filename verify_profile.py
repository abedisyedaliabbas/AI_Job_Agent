"""Verify the updated profile"""
import json

with open('profile.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("Profile Verification")
print("=" * 60)
print(f"\nName: {data['name']}")
print(f"Email: {data['email']}")
print(f"Location: {data['location']}")
print(f"\nEducation: {len(data['education'])} entries")
print(f"Experience: {len(data['experience'])} entries")
print(f"Publications: {len(data['publications'])} entries")
print(f"Presentations: {len(data['presentations'])} entries")
print(f"Awards: {len(data['awards'])} entries")
print(f"Skills: {len(data['skills'])} categories")

if data.get('metrics'):
    print(f"\nMetrics:")
    print(f"  Total Citations: {data['metrics'].get('total_citations', 'N/A')}")
    print(f"  h-index: {data['metrics'].get('h_index', 'N/A')}")

if data.get('research_interests'):
    print(f"\nResearch Interests: {len(data['research_interests'])}")
    for interest in data['research_interests']:
        print(f"  - {interest}")

print(f"\nPublications by year:")
pub_years = {}
for pub in data['publications']:
    year = pub.get('year', 'Unknown')
    pub_years[year] = pub_years.get(year, 0) + 1

for year in sorted(pub_years.keys(), reverse=True):
    print(f"  {year}: {pub_years[year]} publications")

print("\n" + "=" * 60)
print("[OK] Profile verification complete!")
print("=" * 60)
