function onSubmitForm(e) {
    var formAttributes = e.response.getItemResponses();
    sendFormDataToGitHub(formAttributes);
}

function decodeBase64(base64String) {
    var decodedBytes = Utilities.base64Decode(base64String);
    return Utilities.newBlob(decodedBytes).getDataAsString();
}

function sendFormDataToGitHub(formAttributes) {
    const scriptProperties = PropertiesService.getScriptProperties();
    const githubToken = scriptProperties.getProperty('GITHUB_TOKEN');

    var owner = scriptProperties.getProperty('GH_REPO_OWNER');
    var repo = scriptProperties.getProperty('GH_REPO');
    var filePath = 'users.json';

    var formData = {}
    for (var i = 0; i < formAttributes.length; i++) {
        var attribute = formAttributes[i];
        var name = attribute.getItem().getTitle();
        formData[name] = attribute.getResponse();
    }

    Logger.log("formAttributes");
    Logger.log(formData);
    var apiUrl = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + filePath;
    var response = UrlFetchApp.fetch(apiUrl, {
        headers: {
            Authorization: 'Bearer ' + githubToken
        },
        muteHttpExceptions: true
    });
    var fileInfo = JSON.parse(response.getContentText());
    Logger.log("fileInfo");
    Logger.log(fileInfo);
    var sha = fileInfo.sha;

    Logger.log(fileInfo.content);
    Logger.log("fileInfo.content");

    var currentContent = decodeBase64(fileInfo.content);
    Logger.log("currentContent");
    Logger.log(currentContent);
    Logger.log("formData");
    Logger.log(formData);

    var updatedContent;
    var existingData;
    try {
        if (currentContent) {
            // If file exists and contains valid JSON data
            Logger.log("currentContent.toString()");
            Logger.log(currentContent.toString());
            existingData = JSON.parse(currentContent);
            Logger.log("existingData");
            Logger.log(existingData);
            if (!Array.isArray(existingData)) {
                throw new Error('Invalid existing JSON data');
            }
            existingData.push(formData);
        } else {
            // If file doesn't exist, create new JSON array with form data
            existingData = [formData];
        }
        updatedContent = JSON.stringify(existingData);
    } catch (error) {
        // Handle JSON parsing errors
        Logger.log('Error parsing existing JSON content: ' + error);
        return;
    }

    var encodedContent = Utilities.base64EncodeWebSafe(updatedContent);

    // Prepare request options
    var options = {
        method: 'PUT',
        headers: {
            Authorization: 'Bearer ' + githubToken,
            'Content-Type': 'application/json'
        },
        payload: JSON.stringify({content: encodedContent, sha: sha, message: 'Update form data'})
    };

    // Send request to GitHub API
    var apiUrl = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + filePath;
    Logger.log(apiUrl);
    var response = UrlFetchApp.fetch(apiUrl, options);

    // Log response
    Logger.log(response.getContentText());
}
