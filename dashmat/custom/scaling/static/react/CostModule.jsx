import React, {Component, PropTypes} from 'react';
import WidgetBox from '/modules/dashmat.core_modules.components/WidgetBox.jsx';

export default class CostModule extends WidgetBox {
  render_inner() {
    return (
      <div>
        <div style={{padding: "5px"}}>
          <h3>{this.props.title}</h3>
          {this.state.data.cost.map((v, index) =>
            <p key={index}>{v[0]}: {v[1]}</p>
          )}
        </div>
      </div>
    )
  }
}

CostModule.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    cost: PropTypes.object,
  }),
  title: PropTypes.string,
};
