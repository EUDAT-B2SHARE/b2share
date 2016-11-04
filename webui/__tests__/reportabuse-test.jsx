import { ReportAbuse } from '../src/components/reportabuse';
import { serverCache, notifications, browser } from '../src/data/server.js';
import { shallow } from 'enzyme';
import React from 'react/lib/ReactWithAddons';
import { shallowToJson } from 'enzyme-to-json';
import ReactTestUtils from 'react-addons-test-utils';


describe('Report abuse form', () => {
	const id = '1033083fedf4408fb5611f23527a926d';
	const component = shallow(<ReportAbuse params={{ id: '1033083fedf4408fb5611f23527a926d' }} />);

	const st = require.requireActual('../src/data/server', ()=> ({serverCache: {reportAbuse: jest.fn()}}));
	st.reportAbuse = jest.fn();

    // var spy = jest.mock('../src/data/server', ()=> ({serverCache: {reportAbuse: jest.fn()}}));



	it('shall have 4 radiobuttons named reason', () => {
		expect(component.find('#reason').length).toEqual(4);
		expect(shallowToJson(component)).toMatchSnapshot();
	});
	

	it('shall have a send button', () => {
		expect(component.find('#send').length).toEqual(1);
		expect(shallowToJson(component)).toMatchSnapshot();
	});


	it('sends the form correctly', ()=> {
		var data = {copyright:true, message: 'test message', name:'ttt', affiliation:'affiliation_test', email:'test@t.com', address:'ajhdj jdjasd ahd ka', city:'stockholm', country:'sweden', zipcode:'12345', phone: '8735382073'}
		const button = component.closest('button');
		const copyright = component.closest('#copyright');
		const message = component.closest('#message');
		const name = component.closest('#name');
		const affiliation = component.closest('#affiliation');
		const email = component.closest('#email');
		const address = component.closest('#address');
		const city = component.closest('#city');
		const country = component.closest('#country');
		const zipcode = component.closest('#zipcode');
		const phone = component.closest('#phone');

		// copyright.simulate('change', { target: { value: true } });
		// message.simulate('change', { target: { value: 'my message' } });
		name.simulate('change', { target: { value: 'ttt' } });
		affiliation.simulate('change', { target: { value: 'affiliation_test' } });
		email.simulate('change', { target: { value: 'test@t.com' } });
		address.simulate('change', { target: { value: 'ajhdj jdjasd ahd ka' } });
		city.simulate('change', { target: { value: 'stockholm' } });
		country.simulate('change', { target: { value: 'sweden' } });
		zipcode.simulate('change', { target: { value: '12345' } });
		phone.simulate('change', { target: { value: '8735382073' } });
		button.simulate('click');


		// expect(spy).toBeCalledWith(id, data,
		// expect(serverCache.reportAbuse).toBeCalledWith(id, data,
		expect(st.reportAbuse).toBeCalledWith(id, data,	
			() => {
                browser.gotoRecord(id);
                notifications.success("The abuse report has been successfully sent");
            },
            () => {
                notifications.danger("The abuse report could not be sent. " +
                                     "Please try again or consult the site administrator");
                component.setState({ sending:false });
            });

		expect(shallowToJson(component)).toMatchSnapshot();
	});

});