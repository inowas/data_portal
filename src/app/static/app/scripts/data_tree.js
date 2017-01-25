$(document).ready(function () {
    var apiURL = "/api/dataset-tree/"
    var datasetsURL = "/dataset-details/"
    var objectsURL = "/feature-details/"
    var propertiesURL = "/property-details/"
    var currentURL = window.location.toString().split("/");
    var datasetID = Number(currentURL.slice(-1)[0]);
    console.log({{ dataset.id }})
    $.getJSON(apiURL + "2" + "?format=json", createTree);

    function createTree(data){
        
        var json = data;
        var tree = [];
        for (var k in json) {
            var dataset = json[k]
            tree.push(
                {
                    "text": "Dataset: " + dataset["name"],
                    "href": datasetsURL + dataset["id"],
                    "nodes": []
                }
            )
        
            for (var i in dataset["model_objects"]) {
                var object = dataset["model_objects"][i]
                tree[k]["nodes"].push(
                    {
                        "text": "Object: " + object["name"],
                        "href": objectsURL + object["id"],
                        "nodes": [],
                        "state": {
                            "checked": false,
                            "disabled": false,
                            "expanded": false,
                            "selected": false
                        }
                    }
                )
                
                for (var j in object["properties"]) {
                    var property = object["properties"][j]
                    tree[k]["nodes"][i]["nodes"].push(
                        {
                            "text": "Property: " + property["name"],
                            "href": propertiesURL + property["id"]
                        }
                    )
                }
            }
        }
        var options = {
            bootstrap2: false, 
            showTags: true,
            levels: 5,
            enableLinks: true,
            data: tree
        };
        $('#treeview').treeview(options);
    }
});