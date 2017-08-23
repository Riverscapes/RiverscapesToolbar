// Custom JS Goes HERE
$(document).ready(function (){

	/**
	 * Create a tree out of a flat path recursively.
	 * @param  {[type]}
	 * @param  {[type]}
	 * @param  {[type]}
	 * @return {[type]}
	 */
	// Now place each item in the tree
	function treeize(pages){
		var t = { leaves: [], branches: [] }
		
		for (i in pages) {
			
			var urlArr = pages[i].url.split('/');
			var currLevel = urlArr.shift();
			var pointer = t;

			// Now loop until we're deep enough
			while (urlArr.length > 1) {
				var key = urlArr[0].length == 0 ? "EMPTY" : urlArr[0];
				key = key.replace("_"," ").replace("%20", " ");
				var newDir = null;

				var thebranch = pointer.branches.filter(br => br.key == key)
				if (thebranch.length > 0){
					newDir = thebranch[0];
				}
				else {
					newDir = { key: key, leaves: [], branches: [] }
					pointer.branches.push(newDir);					
				}
				pointer = newDir;
				currLevel = urlArr.shift();
			}
			if (urlArr[0] == "index.html" || urlArr[0] == ""){
				pointer.title = pages[i].title;
				pointer.index = pages[i];
			}
			else{
				pointer.title = pointer.key;
				pointer.leaves.push(pages[i]);				
			}			
		}	
		traverseandsort(t)
		return t
	}

	/**
	 * recursively sort a tree by weight then by alphabet
	 * @param  {[type]}
	 * @return {[type]}
	 */
	function traverseandsort(t) {
		// Now sort branches at this level
		t.branches.sort(function(a,b) {
			a.weight = a.index && a.index.weight ? parseInt(a.index.weight) : 999;
			b.weight = b.index && b.index.weight ? parseInt(b.index.weight) : 999;

			if (a.weight == b.weight) {
				return a.title < b.title ? -1 : (a.title > b.title ? 1 : 0);
			}
			else {
				return a.weight < b.weight ? -1 : (a.weight > b.weight ? 1 : 0);
			}
			return true;
		});

		// Sort the leaves by weight and then by title
		t.leaves.sort(function(a, b) {

			a.weight = parseInt(a.weight) || 999;
			b.weight = parseInt(b.weight) || 999;
			
			if (a.weight == b.weight) {
				return a.title < b.title ? -1 : (a.title > b.title ? 1 : 0);
			}
			else {
				return a.weight < b.weight ? -1 : (a.weight > b.weight ? 1 : 0);
			}
		});


		// Now go find more branches to sort their leaves
		for (br in t.branches) {
			traverseandsort(t.branches[br])
		}
	}	

	/**
	 * Turn a tree structure from treeize into a topbar
	 * @param  {[type]}
	 * @return {[type]}
	 */
	function topbarize(tree, title) {
		var $topbar = $('<div class="top-bar"></div>');
		var $topbarleft = $('<div class="top-bar-left"></div>');
		$topbar.append($topbarleft);
		var $title = $('<li><a href="'+NAVHome+'">'+NAVTitle+'</li>');

		function menutraverse(t, $mUL) {
			if (!$mUL) {
				$mUL = $('<ul class="dropdown menu" data-dropdown-menu></ul>');
				$mUL.append($title);
			}
			// Now go find more branches to sort their leaves
			for (lf in t.leaves) {
				$li = $('<li><a href="' + t.leaves[lf].absurl + '">' + t.leaves[lf].title + '</a></li>');
				$mUL.append($li);
			}				
			// Now go find more branches to sort their leaves
			for (br in t.branches) {
				$newmLi = $('<li></li>');
				$newmA = $('<a href="#">'+ br +'</a>');
				$newmUl = $('<ul class="menu vertical"></ul>');
				$newmLi.append($newmA);
				$newmLi.append($newmUl);
				$mUL.append($newmLi);
				menutraverse(t.branches[br], $newmUl);
			}
			return $mUL;			
		}

		$topbarleft.append(menutraverse(tree));
		return $topbar
	}

	/**
	 * Turn a tree structure from treeize into a topbar
	 * @param  {[type]}
	 * @return {[type]}
	 */
	function accordionize(t, $mUL) {
		if (!$mUL) {
			$mUL = $('<ul id="topmenu" class="vertical menu accordion-menu" data-accordion-menu data-submenu-toggle="true"></ul>');
		}
		// Now go find more branches to sort their leaves
		for (lf in t.leaves) {
			$li = $('<li class="leaf"><a href="' + t.leaves[lf].absurl + '"><i class="icon"/>' + t.leaves[lf].title + '</a></li>');
			var extSplit = t.leaves[lf].url.split('.');
			if (extSplit.length == 1 || extSplit[extSplit.length -1] == "html") 
				$mUL.append($li);
		}				
		// Now go find more branches to sort their leaves
		for (brind in t.branches) {
			$newmLi = $('<li class="branch"></li>');
			var br = t.branches[brind];

			if (br.index){
				$newmA = $('<a class="reallink" href="' + br.index.absurl + '"><i class="icon"/>' + br.index.title + '</a>');
			}
			else{
				$newmA = $('<a class="nolink" href="#"><i class="icon"/>'+ br.title +'</a>');
			}
			$newmUl = $('<ul class="menu vertical nested"></ul>');
			$newmLi.append($newmA);
			$newmLi.append($newmUl);
			$mUL.append($newmLi);
			accordionize(br, $newmUl);
		}
		return $mUL;			
	}

	function expandCurentAccordion($sidebar) {
		$menuEl = $sidebar.find("[href='"+window.location.pathname+"']");
		$menuEl.addClass('menuActive');

		$immediateChild = $menuEl.parent().find('ul');
		$immediateChild.addClass('menuActive');
		$sidebar.foundation('down', $immediateChild);
		
		menuancestry = $menuEl.parentsUntil($sidebar);
		menuancestry.each(function(key, val){
			$sidebar.foundation('down', $(val));
		})
	}

	// Do all the things to get the tree
	tree = treeize(NAVPages);
	$topbar = topbarize(tree);
	$sidebarnav = accordionize(tree);

	$('#topbarnav').append($topbar);
	$('#sidenav').append($sidebarnav);

	// Initialize our UI framework
	$(document).foundation();
	expandCurentAccordion($sidebarnav);

	// Rewrite a few of the interactions with the menu3
	$('#topmenu i.icon').click(e => {
			e.stopPropagation();
			e.preventDefault();
			$(e.toElement).parent().siblings('button').click();
	})
	$('#topmenu li.branch a.nolink').click(e => {
		e.preventDefault();
		$(e.toElement).siblings('button').click();
})
	
	// Bind our buttons to menu actions
	$('#menuCtls #expand').click(function(){
		$sidebarnav.foundation('showAll');
	});
	$('#menuCtls #contract').click(function(){
		$sidebarnav.foundation('hideAll');
		expandCurentAccordion($sidebarnav);
	});

	$('#toc').toc();
	$('#toc').prepend('<h4><span class="fa fa-file-text"></span> Page Contents:</h4>')

});
