function onSubmitForm(e) {
    var formAttributes = e.response.getItemResponses();
    sendFormDataToGitHub(formAttributes);
}

function decodeBase64(base64String) {
    var decodedBytes = Utilities.base64Decode(base64String);
    return Utilities.newBlob(decodedBytes).getDataAsString();
}


function sendApiRequest(username, password, coupon, pyvista) {
    var url = "https://4y6bjkv5z0.execute-api.us-east-2.amazonaws.com/";
    var headers = {
        "Content-Type": "application/json"
    };

    var payload = {
        "username": username,
        "password": password,
        "pyvista": pyvista,
        "coupon": coupon
    };

    var options = {
        "method": "post",
        "headers": headers,
        "payload": JSON.stringify(payload)
    };

    Logger.log("payload");
    Logger.log(payload);
    var response = UrlFetchApp.fetch(url, options);

    // Handle the response
    var responseData = JSON.parse(response.getContentText());
    Logger.log("responseData");
    Logger.log(responseData);
}


function sendFormDataToGitHub(formAttributes) {
    var formData = {}
    for (var i = 0; i < formAttributes.length; i++) {
        var attribute = formAttributes[i];
        var name = attribute.getItem().getTitle();
        formData[name] = attribute.getResponse();
    }
    Logger.log("formAttributes");
    Logger.log(formData);
    var Username = formData['Username']
    var Password = formData['Password']
    var Coupon = formData['Coupon']
    var PyvistaVal = formData['Attending PyVista Tutorial?']

    var Pyvista = false
    if (PyvistaVal.toLowerCase() === "yes") {
        Pyvista = true;
    }
    sendApiRequest(Username, Password, Coupon, Pyvista)
}
