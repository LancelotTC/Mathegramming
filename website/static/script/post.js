function commentVote(commentId, voteResult) {
	fetch(
		"/comment_vote",
		{ method: "POST", body: JSON.stringify({ commentId: commentId, voteResult: voteResult }) })
		.then((_res) => { window.location.href = ""; })
}

function postVote(postId, voteResult) {
	fetch(
		"/post_vote",
		{ method: "POST", body: JSON.stringify({ postId: postId, voteResult: voteResult }) })
		.then((_res) => { window.location.href = ""; })
}
