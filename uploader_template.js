$("#zoology_zoology_geom").val("{geo_str}")
$("#zoology_zoology_date_day").val({day})
$("#zoology_zoology_date_month").val({month})
$("#zoology_zoology_date_year").val({year})
$("#zoology_zoology_timefrom_hour").val({hour})
$("#zoology_zoology_timefrom_minute").val({minute})
$("#zoology_zoology_timeto_hour").val({hour_to})
$("#zoology_zoology_timeto_minute").val({minute_to})
document.getElementById("zoology_zoology_description_ifr").contentWindow.document.getElementById("tinymce").innerHTML = "{text}" // poznamka k lokalite
$("#zoology_lkpsky_id").val({sky_condition_level})
$("#zoology_lkpwind_id").val({wind_level})
$("#zoology_lkptemperature_id").val({temperature_level})

all_species_data = {bird_records}
counter = 1
for (species_data of all_species_data) {{
	if (counter > 1) {{
		$("#sf_fieldset_none > div.detailsFieldset > table > tbody > tr > td > div > div.content > div.help > a").click()
		await new Promise(r => setTimeout(r, 500));
	}}
	$("#zoology_detail_" + counter + "_lkpzoospecies_id").val(species_data["species_id"])
	$("#autocomplete_zoology_detail_" + counter + "_lkpzoospecies_id").val(species_data["name"])
	$("#zoology_detail_" + counter + "_count").val(species_data["count"])
	$("#zoology_detail_" + counter + "_lkpzoochar_id").val(species_data["observation_characteristic"])

	$(".sf_admin_form_field_detail" + counter + " #mytgb").click()
	$("#zoology_detail_" + counter + "_lkpzoomet_id").val(species_data["observation_method"])
	if (species_data["note"] != '') {{
		$("#zoology_detail_" + counter + "_description").val(species_data["note"])
	}}

	counter += 1
}}
