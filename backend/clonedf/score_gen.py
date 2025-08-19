import json




def score_calc():

    file_name = 'semgrep_results_analyzed.json'
    with open(file_name, 'r') as f:
        data = json.load(f)

    total_count = 0
    results_list = data['results']
    vuln_count =0

    for result in results_list:
        impact_value = result['extra']['metadata']['impact']
        vuln_count+=1 
        if impact_value == "HIGH":
            total_count += 10
        elif impact_value == "MEDIUM":
            total_count += 6
        elif impact_value == "LOW":
            total_count += 3

    score = int((total_count/(vuln_count*10))*100)
    return score    
        

score_calc()
