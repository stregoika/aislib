-- Function: ce_fisheries.prueba()

-- DROP FUNCTION ce_fisheries.prueba();

CREATE OR REPLACE FUNCTION ce_fisheries.prueba()
  RETURNS void AS
$BODY$DECLARE    
   cVessel CURSOR FOR 
      SELECT DISTINCT ON (cfr) vessel_raw.* 
      FROM ce_fisheries.vessel_raw
      ORDER BY cfr, import_date DESC, event_end_date DESC
      ; /* LIMIT 5 temporal para no saturarme*/
   regVessel ce_fisheries.vessel_raw%ROWTYPE;
   regVesselClean ce_fisheries.vessel%ROWTYPE;
   eventOut varchar[] := array['DES', 'RET', 'EXP'];
BEGIN
   FOR regVessel IN cVessel LOOP
      RAISE NOTICE 'CFR: %  ; ID: % ; EVENT: %', regVessel.cfr, regVessel.id, 
                                                 regVessel.event_code;
      IF NOT EXISTS (SELECT 1 FROM ce_fisheries.vessel
                     WHERE ce_fisheries.vessel.cfr = regVessel.cfr)
         THEN
         INSERT INTO ce_fisheries.vessel 
            (id, country_code, cfr, active, reg_num, ext_marking, vessel_name, 
             port_code, port_name, ircs_code, ircs, vms_code, gear_main_code, 
   	     gear_sec_code, loa, lbp, ton_ref, ton_gt, ton_oth, ton_gts, power_main,
   	     power_aux, hull_material, com_year, com_month, com_day, segment, 
   	     construction_year, construction_place, import_date) 
         VALUES
            (regVessel.id, regVessel.country_code, regVessel.cfr, 
             CASE 
                 WHEN regVessel.event_code != ALL (eventOut) THEN 'Y'
                 ELSE 'N'
             END, 
             regVessel.reg_num, regVessel.ext_marking, regVessel.vessel_name, 
             regVessel.port_code, regVessel.port_name, regVessel.ircs_code,
   	     regVessel.ircs, regVessel.vms_code, regVessel.gear_main_code, 
   	     regVessel.gear_sec_code, 
             to_number(replace(regVessel.loa,',',','),'9999D99'), 
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
   ELSE
      RAISE NOTICE 'Este CFR ya existe en vessel % ', regVessel.cfr;
      SELECT * INTO regVesselClean 
      FROM ce_fisheries.vessel 
      WHERE ce_fisheries.vessel.cfr=regVessel.cfr;
      RAISE NOTICE 'CFR: %  ; ID: % ; ACTIVO: %', regVesselClean.cfr, 
                                                  regVesselClean.id, 
                                                  regVesselClean.active;
      UPDATE ce_fisheries.vessel as v
      SET v.id = regVessel.id,
          v.country_code = regVessel.country_code, 
          v.cfr = regVessel.cfr, 
          v.active = (CASE 
                          WHEN regVessel.event_code != ALL (eventOut) THEN 'Y'
                          ELSE 'N'
                          END), 
          v.reg_num = regVessel.reg_num, 
          v.ext_marking = regVessel.ext_marking, 
          v.vessel_name = regVessel.vessel_name, 
          v.port_code = regVessel.port_code, 
          v.port_name = regVessel.port_name, 
          v.ircs_code = regVessel.ircs_code, 
          v.ircs = regVessel.ircs, 
          v.vms_code = regVessel.vms_code, 
          v.gear_main_code = regVessel.gear_main_code, 
   	  v.gear_sec_code = regVessel.gear_sec_code, 
   	  v.loa = regVessel.loa, 
   	  v.lbp = regVessel.lbp, 
   	  v.ton_ref = regVessel.ton_ref, 
   	  v.ton_gt = regVessel.ton_gt, 
   	  v.ton_oth = regVessel.ton_oth, 
   	  v.ton_gts = regVessel.ton_gts, 
   	  v.power_main = regVessel.power_main,
   	  v.power_aux = regVessel.power_aux, 
   	  v.hull_material = regVessel.hull_material, 
   	  v.com_year = regVessel.com_year, 
   	  v.com_month = regVessel.com_month, 
   	  v.com_day = regVessel.com_day, 
   	  v.segment = regVessel.segment, 
   	  v.construction_year = regVessel.construction_year, 
   	  v.construction_place = regVessel.construction_place, 
   	  v.import_date = regVessel.import_date
      WHERE v.cfr = regVessel.cfr;
   END IF;
   END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION ce_fisheries.prueba()
  OWNER TO postgres;

