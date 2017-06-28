# VCRM application


## Elements

- Circle
- Light
- Sphere

### Circle

Parameter:  
`radius` unit: mm  
`center` pass(x, y) to the first parameter; OR pass x, y to each parameter.  

method:  
`on_circle` pass `point`, `tol=1e-5` to method `tol` means the accuracy

### Light

Parameter:  
`wavelength`  
`direction` : a vector, instance of Vec2d or Vec3d  
`refraction_index` : refraction index outside the particle  
`unit` : the unit of the wavelength   


## Functions

- tangential_vector_to_circle
- intersection
- pick_start_points
- ref_factors
- reflction
- refraction


## 3D funcs

## Functions

- drawer  
- multi_line_drawer  

### drawer

Single light drawer.  
Parameter:  
`sphere` : One of the intersectionElements class. Define the sphere with certain radius and center  
`incident_light` : One of the intersectionElements class. see Elements about light  
`refraction_index` :  the refraction index of the paticle  
`start_point` : The coordinates of the starting point. Tuple or list contains three float numbers  
`intersection_time` ; Times of the intersection, How many times the light intersect the sphere  

Return:  
`dict`    
`points: the intersection points` `list`  first intersection: points[0] second intersection point: points[1] etc.  
`lines: the lines to draw in the figre` `list`   

### multi_line_drawer  

calculate and return points and lines with given a list of start points and incident lights.  

Parameter:  
`sphere` : incident of the class `Sphere`  
`incident_light` : incident of class `Light`  
`refraction_index` : the refraction index of the paticle  
`start_point_list` : a list that contains the coordiates of the start points  
`intersection_time` : How many times the light intersect the sphere  

Return:  
`dict`  
`points` : `list` of the intersection points  
`lines` : `dict` of the refraction lines and reflection lines  
`lights` : `dict` of the reflection lights and refraction lights  