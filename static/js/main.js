String.format = function (string, obj) {
    return string.replace(/{([^}]+)}/g, function(m, thing) {
        return typeof obj[thing] != 'undefined' ? obj[thing] : m
    })
}

FORMAT = `<li class="collection-item flex-dynamic">
        <a target="_blank" href="{url}">{subject}</a>
        <span class="project-name">{project}</span>
</li>
`;

function parseGerritDate(s) {
    let res = new Date();
    // 2017-02-09 00:42:30.000000000
    let parts = s.split(" ");
    let date = parts[0].split("-");
    res.setUTCFullYear(Number(date[0]));
    res.setUTCMonth(Number(date[1])-1);
    res.setUTCDate(Number(date[2]));
    let hms = parts[1].split(":");
    res.setUTCHours(Number(hms[0]));
    res.setUTCMinutes(Number(hms[1]));
    res.setUTCSeconds(Number(hms[2]));
    return res;
}

function shouldPutBuildLabel(last, next, buildDate) {
    return (last == -1 || last >= buildDate) && next <= buildDate
}

currentBuildIndex = 0;
changesUpdated = [];
prevChangeTime = -1;
function renderChanges(data, textStatus, xhr) {
    var res = []
    let now = Date.now() / 1000;

    // Gerrit returns a list of changes sorted by "update date", while we
    // need a list sorted by "submit date". Remove the changes positioned
    // incorrectly from the list and insert them as soon as we find a change
    // with an older "submit date".
    for (var el in data.res) {
        if (data.res[el].updated == null || data.res[el].submitted == null) {
            continue;
        }
        if (data.res[el].updated != data.res[el].submitted) {
            var i = 0;
            for (; i < changesUpdated.length; i++) {
                if (changesUpdated[i].submitted < data.res[el].submitted) {
                    break;
                }
            }
            changesUpdated.splice(i, 0, data.res[el]);
        } else {
            while (changesUpdated.length > 0) {
                if (data.res[el].submitted < changesUpdated[0].submitted) {
                    res.push(changesUpdated.shift());
                } else {
                    break;
                }
            }
            res.push(data.res[el]);
        }
    }

    for (var el in res) {
        if (!res.hasOwnProperty(el)) {
            continue;
        }
        if (res[el].subject == "Automatic translation import") {
            continue;
        }
        if (res[el].project == null) {
            // Gerrit is down
            document.getElementById("changes").innerHTML += String.format(FORMAT, {'url': res[el].url, 'subject': 'Failed to connect to gerrit', 'project': ''});
            // Don't try and load anything else - leave loading set to true.
            return;
        }
        let date = new Date(res[el].submitted * 1000);
        while (currentBuildIndex >= 0 && currentBuildIndex < builds.length && shouldPutBuildLabel(prevChangeTime, res[el].submitted, builds[currentBuildIndex].datetime)) {
            document.getElementById("changes").innerHTML += String.format('<li class="collection-header"><strong>Changes included in {release}</strong></li>',
                    { 'release': builds[currentBuildIndex].filename });
            currentBuildIndex--;
        }
        lastChangeTime = res[el].submitted - 1;
        prevChangeTime = lastChangeTime;
        let args = {
            'url': res[el].url,
            'subject': res[el].subject,
            'project': res[el].project.split('/')[1],
        };
        document.getElementById("changes").innerHTML += String.format(FORMAT, args);
    }
    loading = false;
    lastChangeTime = data.last - 1;
}

function loadMore() {
    document.getElementById("changes").innerHTML += '<li class="collection-item loading">Loading...</li>';
    $.getJSON('/api/v1/changes/' + device + '/' + lastChangeTime + '/', null, function(data, textStatus, xhr) {
        $('#changes .loading').remove();
        renderChanges(data, textStatus, xhr);
        onScroll(); // if we don't have >1 window of changes, load more
    });
}
builds = [];
loading = false;
$(document).ready(function() {
    loading = true;

    $.getJSON('/api/v1/' + device + '/nightly/changelog', null, function(data, textStatus, xhr) {
        builds = data.response;
        currentBuildIndex = builds.length - 1;
        while (currentBuildIndex >= 0 && currentBuildIndex < builds.length && Date.now() < builds[currentBuildIndex].datetime) {
            console.log('disregarding ' + builds[currentBuildIndex].datetime + ', ' + builds[currentBuildIndex].filename);
            currentBuildIndex--;
        }

        if (device != 'all' && lastChangeTime == -1) {
            document.getElementById("changes").innerHTML += '<li class="collection-header"><strong>Changes to be included in next build</strong></li>';
        }

        loadMore();
    });

    /* all is not actually a device, so the builds endpoint will 404 */
    if (device == 'all') {
        loadMore();
    }

});

function onScroll() {
    if (loading) return;
    // load more within 75px of bottom of the page
    if ($(window).scrollTop() >= $(document).height() - $(window).height() - 75) {
        loading = true;
        loadMore();
    }
}

$(window).scroll(onScroll);

