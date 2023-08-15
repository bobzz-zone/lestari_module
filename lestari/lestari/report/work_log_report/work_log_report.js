// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Work Log Report"] = {
		"filters": [
			{
				"fieldname": "year",
				"label": __("Year"),
				"fieldtype": "Int",
				"default": moment().year(),
				"reqd": 1
			},
			{
				"fieldname": "month",
				"label": __("Month"),
				"fieldtype": "Select",
				"options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
				"default": moment().format("MMMM"),
				"reqd": 1
			},
			{
				"fieldname": "week",
				"label": __("Week"),
				"fieldtype": "Int",
				"default": moment().week(),
				"reqd": 1
			},
			{
				"fieldname": "day",
				"label": __("Day"),
				"fieldtype": "Select",
				"options": "Monday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday",
				"default": moment().format("dddd"),
				"reqd": 1
			}
		],
		"formatter": function (value, row, column, data, default_formatter) {
			if (column.fieldname == "duration") {
				value = value / 60; // convert seconds to minutes
				return Math.round(value * 100) / 100; // round to 2 decimal places
			} else {
				return default_formatter(value, row, column, data);
			}
		},
		"refresh": function (report) {
			var year = report.filters.year.get_value();
			var month = report.filters.month.get_value();
			var week = report.filters.week.get_value();
			var day = report.filters.day.get_value();
			
			var start_date = moment().year(year).month(month - 1).week(week).day(day).toDate();
			var end_date = moment(start_date).add(1, 'week').toDate();
			
			frappe.call({
				method: "frappe.desk.reportview.get",
				args: {
					"doctype": "Work Log",
					"filters": {
						"from_date": frappe.datetime.get_datetime_str(start_date),
						"to_date": frappe.datetime.get_datetime_str(end_date),
						"day_of_week": moment(start_date).day() + 1
					}
				},
				callback: function (r) {
					var data = r.message.values;
					report.report_data = data;
					report.refresh();
				}
			});
		}
	};
	
