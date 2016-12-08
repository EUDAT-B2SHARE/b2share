import { NewRecordRoute } from '../src/components/editrecord';
// import { mount } from 'enzyme';
import { shallow } from 'enzyme';
import React from 'react/lib/ReactWithAddons';

jest.mock('react-dom');
//jest.mock('');
jest.mock('react/lib/ReactDefaultInjection');
//jest.mock('react/lib/ReactMount');
// jest.mock('react-dom');



describe('Create new draft button', () => {
	const component = shallow(<NewRecordRoute />);
	it('is rendered correctly', () => {
  		const button = component.find('button').first();
		expect(button).toBeDefined();
	});

	it('returns error if the title or community is empty', ()=>{
		const community_id = 1;
		const title = 'new record';
		const done = jest.fn();
		
		const p = component.find('.new-record'); // or find('new-record')
		expect(p.length).toEqual(1)
		// const p = component.find('errortitle').simulate('click');
		// expect(component.done).toBeCalled();
        // expect(component.done).toHaveBeenCalledTimes(1);
        // expect(component.done).toBeCalledWith({title: title, community_id: community_id});

		// console.log(p);
		// p.simulate('submit');
		// expect(p.text().toBe('Please add a (temporary) record title'));
	});

});