/*
 * This file is part of B2SHARE.
 *
 * B2SHARE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * B2SHARE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */


// The window._ global variable is exported by lodash and used by lindat-license-selector
// but also by invenio to implement internationalization (see translate.js)
// We need to save the lodash implementation in order to use it before calling the license selector

if (window.lodash) {
	// restore _ to lodash
	console.log("restore _ to lodash");
	window._ = window.lodash;
} else if (window._) {
	// save _ to lodash
	console.log("save _ to lodash");
    window.lodash = window._;
}
