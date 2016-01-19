import React, {Component, PropTypes} from 'react';
import WidgetBox from '/modules/dashmat.core_modules.components/WidgetBox.jsx';
import styles from '/modules/dashmat.server/Dashboard.css';

export class CommentsModule extends WidgetBox {
  render() {
    if (this.state.data === undefined) {
      return <p>Waiting...</p>;
    }

    return (
      <flexcontainer>
        {this.state.data.nice_comments.map((c, i) =>
          <div key={i} className={styles.text_widget}>
            <p>{c}</p>
          </div>
        )}
      </flexcontainer>
    )
  }
}

CommentsModule.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    nice_comments: PropTypes.array
  }),
  title: PropTypes.string,
};

