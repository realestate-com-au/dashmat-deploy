import React, {Component, PropTypes} from 'react';
import WidgetBox from '/modules/dashmat.core_modules.components/WidgetBox.jsx';

export default class CostModule extends Component {
  render() {
    return (
      <WidgetBox {...this.props}>
        <div style={{padding: "5px"}}>
          <h3>{this.props.title}</h3>
          {this.props.data.cost.map((v, index) =>
            <p key={index}>{v[0]}: {v[1]}</p>
          )}
        </div>
      </WidgetBox>
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
