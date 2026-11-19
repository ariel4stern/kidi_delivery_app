area_distributions_dict = {
        'driver_id': [2,3,2,2,2,2,3,2,2,1,1,1,1,1,1,1,1,1,
                      1,1,1,1,1,1,2,2,2,
                      1,1,1,1,1,1,1,1,2,2,2,2,2,2,
                      2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,2,2,
                      1,1,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,
                      404,
                      404],
        'day': ['sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday','sunday', 'sunday', 'sunday',
                'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday',
                'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday',
                'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday',
                'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday',
                'wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday',
                'wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday',
                'wednesday', 'wednesday',
                'thursday', 'thursday', 'thursday', 'thursday','thursday', 'thursday', 'thursday', 'thursday',
                'thursday', 'thursday', 'thursday', 'thursday','thursday', 'thursday', 'thursday', 'thursday',
                'thursday', 'thursday', 'thursday', 'thursday',
                'friday',
                'saturday'],
        'points': [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37,
                 17,21,24,25,34,39,22,26,1,
                 1,6,9,12,16,43,704,705,11,14,19,29,35,708,
                 3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37,22,26,
                 1,6,9,12,16,43,704,705,11,14,19,29,35,708,17,21,24,25,34,39,
                 404,
                 404]


}

print([len(area_distributions_dict[key]) for key,item in area_distributions_dict.items()])


