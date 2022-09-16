text = "rybarik 2x sedi na trstine pri Ciernej vode"
lat = 17.469024641149367
lon = 48.3266521
geo_str = "POINT(" + lat + " " + lon + ")"
day = 1
month = 9
year = 2022
hour = 10
minute = 33
duration_minutes = 2


$("#zoology_zoology_geom").val(geo_str)
$("#zoology_zoology_date_day").val(day)
$("#zoology_zoology_date_month").val(month)
$("#zoology_zoology_date_year").val(year)
$("#zoology_zoology_timefrom_hour").val(hour)
$("#zoology_zoology_timefrom_minute").val(minute)
$("#zoology_zoology_timeto_hour").val(hour) // osetrit prechod cez hodiny!
$("#zoology_zoology_timeto_minute").val(minute + duration_minutes)
$("#tinymce").innerHTML = "<p>" + text + "</p>" // poznamka k lokalite


sky_condition_levels = {
	"jasno (obloha úplne bez oblačnosti)": 1,
	"polojasno (veľká väčšina oblohy bez oblačnosti)": 2,
	"polooblačno (asi polovica oblohy je pokrytá oblačnosťou)": 3,
	"oblačno (väčšina oblohy je pokrytá oblačnosťou)": 4,
	"zamračené (obloha je úplne pokrytá oblačnosťou)": 5,
	"hmla / zamračené nízkou inverznou oblačnosťou (na horách jasno)": 6
}
sky_condition = "polojasno (veľká väčšina oblohy bez oblačnosti)"
$("#zoology_lkpsky_id").val(sky_condition_levels[sky_condition])


wind_levels = {
	"bezvetrie": 1,
	"slabý vietor (vietor pohybuje iba listami na stromoch, ale nie konármi)": 2,
	"mierny vietor (vietor už pohybuje aj konármi stromov)": 3,
	"silný vietor (vietor pohybuje celým stromom, môže dochádzať k odlamovaniu konárov)": 4,
	"víchrica (na stromoch sa odlamujú veľké konáre, alebo sa vyvracajú celé stromy)": 5
}
wind_level = "bezvetrie"
$("#zoology_lkpwind_id").val(wind_levels[wind_level])

counter = 1
for (species_data of all_species_data) {
	if (counter > 1) {
		$("#sf_fieldset_none > div.detailsFieldset > table > tbody > tr > td > div > div.content > div.help > a").click()
	}
	species_id = 3580
	species_count = 2
	species_name = "krakla"
	$("#zoology_detail_" + counter + "_lkpzoospecies_id").val(species_id)
	$("#zoology_detail_" + counter + "_count").val(species_count)
	$("#autocomplete_zoology_detail_" + counter + "_lkpzoospecies_id").val(species_name)
	counter += 1
}
