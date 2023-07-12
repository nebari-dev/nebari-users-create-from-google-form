//  Google Apps Script script that handles form submissions and sends data to a
//  Lambda function using an HTTP POST request.

function onSubmitForm(e) {
    var formAttributes = e.response.getItemResponses();
    sendFormDataToLambda(formAttributes);
}

function sendApiRequest(username, password, coupon, pyvista) {
    const scriptProperties = PropertiesService.getScriptProperties();
    const url = scriptProperties.getProperty('LAMBDA_URL');
    const auth_key = scriptProperties.getProperty('LAMBDA_AUTH_KEY');
    var headers = {
        "Content-Type": "application/json"
    };

    var payload = {
        "username": username,
        "password": password,
        "pyvista": pyvista,
        "coupon": coupon,
        "auth_key": auth_key,
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


function sendFormDataToLambda(formAttributes) {
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
