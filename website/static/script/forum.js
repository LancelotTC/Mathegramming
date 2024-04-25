// $(document).ready(function() {
// 	$('input[type=radio][value={{filter["date"][1]}}]').prop("checked", true);
// 	$('input[type=radio][value={{filter["subject"][1]}}]').prop("checked", true);
// 	$('input[type=radio][value={{filter["category"][1]}}]').prop("checked", true);
// 	$('input[type=radio').change(function() {
// 		var form = $('<form method="post" action="/forum"></form>');
// 		$('input[type="radio"]:checked').each(function() {
// 			var value = $(this).val();
// 			form.append('<input type="hidden" name="value" value="' + value + '">');
// 		});
// 		// $('input[id="searches"]').each(function() {
// 		// 	var value = $(this).val();
// 		// 	form.append('<input type="hidden" name="search" value="' + value + '">');
// 		// });
// 		$('body').append(form);
// 		form.submit();
// 	});



// 	// $('button#search-question').click(function() {
// 	// 	var form = $('<form method="post" action="/forum"></form>');
// 	// 	$('input[type="radio"]:checked').each(function() {
// 	// 		var value = $(this).val();
// 	// 		form.append('<input type="hidden" name="value" value="' + value + '">');
// 	// 	});


// 	// 	form.append('<input type="hidden" name="search" value="' + $('#searches').val() + '">')
// 	// 	$('body').append(form);
// 	// 	form.submit();
// 	// 	body.submit()
// 	// });

// });

// function sendRequest() {
// 	fetch(
// 		"/forum",
// 		{method: "POST", body: JSON.stringify({notifId: $('input[type="radio"]:checked').val()})})
// 		.then((_res) => {window.location.href = "";}
// 	)
// }


// $(document).ready(function() {

// })


// window.onload = function() {
// 	const radioButtons = document.querySelectorAll('input[type="radio"]');
// 	const entry = document.getElementById("search")
// 	console.log(radioButtons)
// 	console.log(entry)

// 	radioButtons.forEach(radioButton => {
// 		radioButton.onclick = function() {
// 			console.log(radioButton.value)

// 			radioButtons.forEach(radiobtn => {
// 				if (radiobtn.checked) {
// 					fetch(
// 						"/forum",
// 						{method: "POST", body: JSON.stringify({"radioButton": radioButton.value})})
// 						.then((_res) => {window.location.href = "";}
// 					)
// 				}
// 			})
// 		}
// 	});
// }




window.onload = function () {
	const radioButtons = document.querySelectorAll('input[type="radio"]');
	const entry = document.getElementById("search_query");
	// console.log(radioButtons);
	// console.log(entry);

	radioButtons.forEach(radioButton => {
		radioButton.onchange = function () {

			var checkedValues = {};

			radioButtons.forEach(radiobtn => {
				if (radiobtn.checked && radioButton.className == radiobtn.className) {
					checkedValues[radiobtn.name] = radiobtn.value;
				}
			});
			checkedValues[entry.name] = entry.value;
			fetch("/forum", {
				method: "POST",
				body: JSON.stringify(checkedValues)
			})
				.then((_res) => {
					window.location.href = "";
				});
		};
		entry.onchange = function () {

			var checkedValues = {};

			radioButtons.forEach(radiobtn => {
				if (radiobtn.checked && radioButton.className == radiobtn.className) {
					checkedValues[radiobtn.name] = radiobtn.value;
				}
			});
			checkedValues[entry.name] = entry.value;
			fetch("/forum", {
				method: "POST",
				body: JSON.stringify(checkedValues)
			})
				.then((_res) => {
					window.location.href = "";
				});
		};

	});
};