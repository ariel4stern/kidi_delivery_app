import json

distribution_lines_dict = {
        'day':['sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'],
        'distribution_line':[
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [17,21,24,25,34,39,22,26,1],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708],
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708,17,21,24,25,34,39,22,26],
            [],
            []
        ]
    }
print(len(distribution_lines_dict['distribution_line'][3]),
      len(distribution_lines_dict['distribution_line'][4]))
print(len([1,3,5,6,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36,37,39,43,701,703,704,705,706,707,708,709]))

distribution_lines_zip = list(zip(
    distribution_lines_dict['day'],
    [
        json.dumps(lines, ensure_ascii=False)
        for lines in distribution_lines_dict['distribution_line']
    ]
))
print(distribution_lines_zip)
print(len('saturday'))