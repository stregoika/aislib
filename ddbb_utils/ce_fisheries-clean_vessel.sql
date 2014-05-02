CREATE OR REPLACE FUNCTION ce_fisheries.clean_vessel() 
RETURNS void AS
$BODY$
DECLARE    
    cVessel CURSOR FOR 
        SELECT DISTINCT ON (cfr) vessel_raw.* 
        FROM ce_fisheries.vessel_raw
        ORDER BY cfr, import_date DESC, event_end_date DESC
        LIMIT 500; /*temporal para no saturarme*/
    regVessel ce_fisheries.vessel_raw%ROWTYPE;
    regVesselClean ce_fisheries.vessel%ROWTYPE;
    eventOut varchar[] := array['DES', 'RET', 'EXP']; /*eventos que sacan al barco del registro valido de pesqueros*/
BEGIN
   FOR regVessel IN cVessel LOOP
        /* imprimir mensaje info ultimo evento barco */
       RAISE NOTICE 'CFR: %  ; ID: % ; EVENT: %', regVessel.cfr, regVessel.id, 
                     regVessel.event_code;
        /* si no existe el barco y no es un evento de salida */
       IF NOT EXISTS (SELECT 1 FROM ce_fisheries.vessel
                       WHERE ce_fisheries.vessel.cfr = regVessel.cfr)
	   AND (regVessel.event_code != ALL(eventOut)) THEN
           INSERT INTO ce_fisheries.vessel 
               (id, country_code, cfr, active, reg_num, ext_marking, vessel_name, 
                port_code, port_name, ircs_code, ircs, vms_code, gear_main_code, 
   	        gear_sec_code, loa, lbp, ton_ref, ton_gt, ton_oth, ton_gts, power_main,
   	        power_aux, hull_material, com_year, com_month, com_day, segment, 
   	        construction_year, construction_place, import_date) 
            VALUES
               (regVessel.id, regVessel.country_code, regVessel.cfr, 'Y', 
                regVessel.reg_num, regVessel.ext_marking, regVessel.vessel_name, 
                regVessel.port_code, regVessel.port_name, regVessel.ircs_code,
   	        regVessel.ircs, regVessel.vms_code, regVessel.gear_main_code, 
   	        regVessel.gear_sec_code, 
                to_number(replace(regVessel.loa,',','.'),'9999D99'), 
                regVessel.lbp, 
   	        regVessel.ton_ref, regVessel.ton_gt, regVessel.ton_oth, regVessel.ton_gts,
   	        regVessel.power_main,
   	        regVessel.power_aux,
   	        regVessel.hull_material,
   	        regVessel.com_year,
   	        regVessel.com_month,
   	        regVessel.com_day,
   	        regVessel.segment , 
  	        regVessel.construction_year,
  	        regVessel.construction_place, 
	        regVessel.import_date
               ); 
       /*si ya existe el barco, mirar si hay que actualizar info */
       ELSE
           RAISE NOTICE 'Este CFR ya existe en vessel % ', regVessel.cfr;
           SELECT * INTO regVesselClean 
               FROM ce_fisheries.vessel 
               WHERE ce_fisheries.vessel.cfr=regVessel.cfr;
           /* Ponerlo como inactivo */
           IF regVessel.event_code = ANY(eventOut) AND regVesselClean.active = 'Y' THEN
               UPDATE ce_fisheries.vessel AS V 
               SET
                   id = cVessel.id,
                   country_code = cVessel.country_code,
                   active = 'N',
                   reg_num = cVessel.reg_num,
                   ext_marking = cVessel.ext_marking,
                   vessel_name = cVessel.vessel_name,
                   port_code = cVessel.port_code,
                   port_name = cVessel.port_name,
                   ircs_code = cVessel.ircs_code,
                   ircs = cVessel.ircs,
                   vms_code = cVessel.vms_code,
                   gear_main_code = cVessel.gear_main_code,
                   gear_sec_code = cVessel.gear_sec_code,
                   loa = cVessel.loar,
                   lbp = cVessel.lbp,
                   ton_ref = cVessel.ton_ref,
                   ton_gt = cVessel.
               WHERE cfr = cVessel.cfr;
            END IF;
       END IF;
   END LOOP;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
