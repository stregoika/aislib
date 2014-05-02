CREATE OR REPLACE FUNCTION ce_fisheries.clean_vessel()
RETURNS void AS $$
BEGIN
   INSERT INTO ce_fisheries.vessel 
   (
     	id,
   	country_code,
	cfr,
            active, 
   	reg_num,
   	ext_marking,
   	vessel_name,
   	port_code,
   	port_name,
   	ircs_code,
   	ircs, 
   	vms_code, 
   	gear_main_code, 
   	gear_sec_code,
   	loa, 
   	lbp,
   	ton_ref, 
   	ton_gt,
   	ton_oth,
   	ton_gts,
   	power_main,
   	power_aux,
   	hull_material,
   	com_year,
   	com_month,
   	com_day,
   	segment , 
  	construction_year,
  	construction_place, 
	import_date
   )
SELECT DISTINCT ON (cfr)
(
            id, 
            country_code, 
   	cfr,
           ‘Y’,
   	reg_num,
   	ext_marking,
   	vessel_name,
   	port_code,
   	port_name,
   	ircs_code,
   	ircs, 
   	vms_code, 
   	gear_main_code, 
   	gear_sec_code,
   	loa, 
   	lbp,
   	ton_ref, 
   	ton_gt,
   	ton_oth,
   	ton_gts,
   	power_main,
   	power_aux,
   	hull_material,
   	com_year,
   	com_month,
   	com_day,
   	segment , 
  	construction_year,
  	construction_place, 
	import_date
)
FROM ce_fisheries.vessel_raw
ORDER BY cfr, import_date DESC, event_end_date DESC;
END;
LANGUAGE plpqsql;