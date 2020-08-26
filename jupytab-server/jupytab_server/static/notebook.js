// Copyright (c) 2019 Capital Fund Management
// SPDX-License-Identifier: MIT

$.urlParam = function (name, default_val) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return default_val;
    }
    return decodeURI(results[1]) || 0;
}

function display_notebook_info(kernel_info) {
    $('#notebook-card-info').css("visibility", "visible");
    $('#notebook-info-title').html(kernel_info.name + " (" + kernel_info.kernel_id + ")")
    $('#notebook-info-description').html(kernel_info.description)
    $('#notebook-info-hostname').html(kernel_info.host)
    $('#notebook-info-port').html(kernel_info.port)
    $('#notebook-info-file').html(kernel_info.path)
    $('#notebook-info-status').html(kernel_info.status)
}

function load_notebook_list(token) {
    $.getJSON({
        url: "./api?" + token
    }).done(function (data) {
        $('#notebook-list').empty();
        Object.keys(data).forEach(function (key) {
            $added_item = $('<button type="button" class="list-group-item list-group-item-action"><B>' +
                data[key].name + '</B></button>').appendTo('#notebook-list')

            $added_item.click(function (e) {
                e.preventDefault()
                $(this).parent().find('button').removeClass('active');
                $(this).addClass('active');

                display_notebook_info(data[key])
                define_button_handler(key, token)
            });
        });
    });
}

function explore_in_tableau(active_kernel_id, token) {
    var tableObj = {
        active_kernel_id: active_kernel_id,
        token: token,
    };

    tableau.connectionData = JSON.stringify(tableObj);
    tableau.connectionName = active_kernel_id; // This will be the data source name in Tableau
    tableau.submit(); // This sends the connector object to Tableau
};

function define_button_handler(active_kernel_id, token) {
    $('#restartButton').off('click').click(function () {
        $.getJSON({
            url: "./api/restart/" + active_kernel_id + "?" + token
        }).done(function () {
            load_notebook_list(token);
            $('#notebook-card-info').css("visibility", "hidden");
        })
    });
    $('#submitButton').off('click').click(function () {
        explore_in_tableau(active_kernel_id, token)
    });

    $('#schemaButton').off('click').click(function () {
        window.location.href = "./kernel/" + active_kernel_id + "/schema?" + token
    });
}

$(function () {
    security_token = $.urlParam("security_token", "")

    load_notebook_list("security_token=" + security_token);

    // Create the connector object
    var myConnector = tableau.makeConnector();

    // Define the schema
    myConnector.getSchema = function (schemaCallback) {
        var tableObj = JSON.parse(tableau.connectionData)

        $.getJSON("./kernel/" + tableObj.active_kernel_id + "/schema?" + tableObj.token, function (resp) {
            schemaCallback(resp);
        });
    };

    // Download the data
    myConnector.getData = function (table, doneCallback) {
        let tableObj = JSON.parse(tableau.connectionData)

        let batchSize = 10000

        function load_data(dataChunkIdx) {
            let fromIdx = (dataChunkIdx * batchSize)
            let toIdx = ((dataChunkIdx + 1) * batchSize)

            $.getJSON("./kernel/" + tableObj.active_kernel_id + "/data?table_name=" + table.tableInfo.id + "&" + tableObj.token
            + "&from=" + fromIdx + "&to=" + toIdx + "&refresh=" + (dataChunkIdx == 0 ? "true" : "false")+ "&format=json", function (resp) {
                if(resp.length == 0) {
                    doneCallback();
                } else {
                    tableau.reportProgress("Getting rows " + fromIdx + " to " + (toIdx - 1));
                    let tableData = [];
                    for (let i = 0; i < resp.length; i++) {
                        let row = {}
                        for (let key in resp[i]) {
                            row[key] = resp[i][key]
                        }
                        tableData.push(row);
                    }

                    table.appendRows(tableData);
                    load_data(dataChunkIdx+1)
                }
            });
        }

        load_data(0);
    };

    tableau.registerConnector(myConnector);
});